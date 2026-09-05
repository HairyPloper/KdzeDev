import { createI18n } from 'vue-i18n'
import en from './locales/en.json'

const i18n = createI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en
  },
  legacy: false,
  globalInjection: true
})

export default i18n
