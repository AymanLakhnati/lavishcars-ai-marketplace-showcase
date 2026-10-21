// Local development only. Uses PostgreSQL binaries without installing a service.
import EmbeddedPostgres from "embedded-postgres";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

const databaseDir = resolve(".runtime/postgres");
const pg = new EmbeddedPostgres({
  databaseDir,
  user: "lavish",
  password: process.env.LOCAL_DB_PASSWORD || "lavish_local_only",
  port: Number(process.env.LOCAL_DB_PORT || 54329),
  persistent: true,
  authMethod: "scram-sha-256",
  initdbFlags: ["--encoding=UTF8"],
  postgresFlags: ["-h", "127.0.0.1"],
});
if (!existsSync(resolve(databaseDir, "PG_VERSION"))) await pg.initialise();
await pg.start();
const client = pg.getPgClient();
await client.connect();
const result = await client.query("SELECT 1 FROM pg_database WHERE datname = 'lavish'");
if (!result.rowCount) await client.query("CREATE DATABASE lavish WITH TEMPLATE template0 ENCODING 'UTF8'");
await client.end();
console.log("Local PostgreSQL ready on 127.0.0.1:" + (process.env.LOCAL_DB_PORT || "54329"));
console.log("Database: lavish. Keep this terminal open; Ctrl+C stops PostgreSQL.");
let stopping = false;
async function stop() {
  if (stopping) return;
  stopping = true;
  await pg.stop();
  process.exit(0);
}
process.on("SIGINT", stop);
process.on("SIGTERM", stop);
setInterval(() => {}, 60000);
