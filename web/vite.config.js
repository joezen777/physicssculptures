import {defineConfig} from 'vite';
export default defineConfig({
  build:{
    rollupOptions:{
      input:{main:'index.html',whistle:'whistle.html'},
      onwarn(warning,warn){
        if(warning.code==='MODULE_LEVEL_DIRECTIVE' && warning.message.includes('use client'))return;
        warn(warning);
      },
      output:{manualChunks:{three:['three'],ui:['react','react-dom','@mui/material','@emotion/react','@emotion/styled']}}
    }
  }
});
