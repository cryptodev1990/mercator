import type { ConfigFile } from '@rtk-query/codegen-openapi'

const config: ConfigFile = {
  schemaFile: `${process.env.NEXT_PUBLIC_BACKEND_URL!}/openapi.json`,
  apiFile: './src/store/empty-api.ts',
  apiImport: 'emptySplitApi',
  outputFile: './src/store/search-api.ts',
  exportName: 'searchApi',
  hooks: true,
}

export default config


