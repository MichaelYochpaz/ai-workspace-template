// Injects session-start script output into the system prompt.

import type { Plugin } from "@opencode-ai/plugin";
import { execFile } from "node:child_process";
import { access } from "node:fs/promises";
import { join } from "node:path";

const SCRIPT = ".ai-workspace/scripts/session-start.py";
const SERVICE = "SessionStartPlugin";

type ShellResult = { exitCode: number; stdout: string; stderr: string };

// Node.js fallback for when ctx.$ (Bun shell) is unavailable (e.g. desktop/Electron)
function execNode(command: string, args: string[], cwd: string): Promise<ShellResult> {
  return new Promise((resolve) => {
    execFile(command, args, { cwd, timeout: 10_000, maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
      resolve({
        exitCode: error ? (typeof (error as any).code === "number" ? (error as any).code : 1) : 0,
        stdout: (stdout ?? "").toString(),
        stderr: (stderr ?? "").toString(),
      });
    });
  });
}

export const SessionStartPlugin: Plugin = async (ctx) => {
  const cwd = ctx.directory;
  const scriptPath = join(cwd, SCRIPT);

  async function shell(command: string, args: string[]): Promise<ShellResult> {
    if (ctx.$) {
      const r = await ctx.$`${[command, ...args]}`.cwd(cwd).quiet().nothrow();
      return { exitCode: r.exitCode, stdout: r.text(), stderr: r.stderr.toString() };
    }
    return execNode(command, args, cwd);
  }

  // Cache Promises (not resolved values) to prevent race conditions between
  // session.created and experimental.chat.system.transform firing concurrently
  const cache: Map<string, Promise<string | null>> = new Map();

  async function run(): Promise<string | null> {
    try {
      // Cross-platform file existence check — fs.access works on all OSes,
      // unlike `test -f` which requires a Unix shell or Bun's built-in implementation
      try {
        await access(scriptPath);
      } catch {
        await ctx.client.app.log({
          body: { level: "warn", message: `Session start script not found at ${SCRIPT}`, service: SERVICE }
        });
        return null;
      }

      const result = await shell("uv", ["run", SCRIPT]);
      if (result.exitCode !== 0) {
        const output = (result.stdout + "\n" + result.stderr).trim();
        await ctx.client.app.log({
          body: { level: "warn", message: "Session start script failed", extra: { output }, service: SERVICE }
        });
        return null;
      }

      return result.stdout.trim() || null;
    } catch (err) {
      await ctx.client.app.log({
        body: { level: "error", message: `Session start plugin failed: ${err}`, service: SERVICE }
      }).catch(() => {});
      return null;
    }
  }

  function ensure(id: string): Promise<string | null> {
    const existing = cache.get(id);
    if (existing) return existing;
    const promise = run();
    cache.set(id, promise);
    return promise;
  }

  return {
    event: async ({ event }) => {
      // Defensive: guard against event structure changes
      const id = event.properties?.info?.id;

      if (event.type === "session.created") {
        const parentID = event.properties?.info?.parentID;
        if (parentID && id) {
          // Subagent: share parent's cached result instead of re-running the script
          const parentResult = cache.get(parentID);
          if (parentResult) cache.set(id, parentResult);
          return;
        }
        if (id) ensure(id);
      }

      if (event.type === "session.deleted" && id) {
        cache.delete(id);
      }
    },

    "experimental.chat.system.transform": async (input, output) => {
      if (!input.sessionID) return;
      const result = await ensure(input.sessionID);
      // Defensive: verify output.system is an array before mutating
      if (result && Array.isArray(output.system)) {
        output.system.push(result);
      }
    }
  };
};
