import { rm } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';

// Clean only generated output, so removed pages cannot survive a production build.
await rm(new URL('../_site/', import.meta.url), { recursive: true, force: true });
const preview = process.argv.includes('--preview');
const production = process.argv.includes('--production');
if (preview && production) throw new Error('Choose either --preview or --production.');
const result = spawnSync(process.execPath, ['node_modules/@11ty/eleventy/cmd.cjs'], {
  stdio: 'inherit',
  env: {
    ...process.env,
    ...(preview ? { SITE_PATH_PREFIX: '/katecourtright/', SITE_ENV: 'preview' } : {}),
    ...(production ? { SITE_PATH_PREFIX: '/', SITE_ENV: 'production' } : {}),
  },
});
if (result.error) throw result.error;
process.exit(result.status ?? 1);
