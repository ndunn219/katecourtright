import { spawnSync } from 'node:child_process';

function run(command, args, env) {
  const result = spawnSync(command, args, { stdio: 'inherit', env });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status ?? 1);
}

// End on the root build so the default local preview works immediately afterward.
for (const prefix of ['/katecourtright/', '/']) {
  const env = { ...process.env, SITE_PATH_PREFIX: prefix };
  run(process.execPath, ['scripts/build.mjs'], env);
  run('python3', ['scripts/check_site.py', prefix], env);
}
