import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
// import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'pinkCandyLight',
    themes: {
      pinkCandyLight: {
        dark: false,
        colors: {
          primary: '#E91E63',        // Pink Candy Primary
          secondary: '#9C27B0',      // Purple accent  
          accent: '#FF4081',         // Hot pink accent
          error: '#F44336',          // Red error
          warning: '#FF9800',        // Orange warning
          info: '#2196F3',           // Blue info
          success: '#4CAF50',        // Green success
          surface: '#FFFFFF',        // White surface
          background: '#FDF2F8',     // Very light pink background
          'surface-variant': '#F8BBD9', // Light pink variant
          'on-surface': '#4A148C',   // Dark purple text
          'on-background': '#6A1B9A', // Purple text
          'on-primary': '#FFFFFF',   // White text on primary
          'on-secondary': '#FFFFFF', // White text on secondary
          'on-accent': '#FFFFFF',    // White text on accent
        },
      },
      pinkCandyDark: {
        dark: true,
        colors: {
          primary: '#F48FB1',        // Light pink for dark theme
          secondary: '#CE93D8',      // Light purple
          accent: '#FF80AB',         // Light hot pink
          error: '#EF5350',          // Light red
          warning: '#FFA726',        // Light orange
          info: '#42A5F5',           // Light blue
          success: '#66BB6A',        // Light green
          surface: '#1A1A1A',        // Dark surface
          background: '#121212',     // Dark background
          'surface-variant': '#37474F', // Dark variant
          'on-surface': '#F8BBD9',   // Light pink text
          'on-background': '#FCE4EC', // Very light pink text
          'on-primary': '#4A148C',   // Dark purple on primary
          'on-secondary': '#4A148C', // Dark purple on secondary
          'on-accent': '#4A148C',    // Dark purple on accent
        },
      },
    },
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
})

const app = createApp(App)

app.use(router)
app.use(vuetify)

app.mount('#app')
