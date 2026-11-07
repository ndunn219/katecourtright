import { spawnSync } from 'node:child_process';

function run(command, args, env) {
  const result = spawnSync(command, args, { stdio: 'inherit', env });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status ?? 1);
}

run('python3', ['-m', 'unittest', 'discover', '-s', 'scripts', '-p', 'test_*.py'], process.env);

// End on the root preview so local development stays non-indexable.
for (const [prefix, environment] of [['/katecourtright/', 'preview'], ['/', 'production'], ['/', 'preview']]) {
  const env = { ...process.env, SITE_PATH_PREFIX: prefix, SITE_ENV: environment };
  run(process.execPath, ['scripts/build.mjs'], env);
  run('python3', ['scripts/check_site.py', prefix], env);
  run('python3', ['scripts/check_migration.py', prefix], env);
  run('python3', ['scripts/check_forms.py', prefix], env);
  run(process.execPath, ['scripts/check-interactions.mjs'], env);
}
