// Injects session-start script output into the system prompt.

import type { Plugin } from "@opencode-ai/plugin";

const SCRIPT = ".ai-workspace/scripts/session-start.py";
const SERVICE = "SessionStartPlugin";

export const SessionStartPlugin: Plugin = async (ctx) => {
  const script = SCRIPT;

  // Cache Promises (not resolved values) to prevent race conditions between
  // session.created and experimental.chat.system.transform firing concurrently
  const cache: Map<string, Promise<string | null>> = new Map();

  async function run(): Promise<string | null> {
    const exists = await ctx.$`test -f ${script}`.quiet().nothrow();
    if (exists.exitCode !== 0) {
      await ctx.client.app.log({
        body: { level: "warn", message: `Session start script not found at ${script}`, service: SERVICE }
      });
      return null;
    }

    const result = await ctx.$`uv run ${script}`.quiet().nothrow();
    if (result.exitCode !== 0) {
      await ctx.client.app.log({
        body: { level: "warn", message: "Session start script failed", extra: { output: result.text().trim() }, service: SERVICE }
      });
      return null;
    }

    return result.text().trim() || null;
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
