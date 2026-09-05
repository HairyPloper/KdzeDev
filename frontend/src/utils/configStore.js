import { reactive, watch } from 'vue'

const CONFIG_KEY = 'agent_config_settings'

const defaultSettings = {
    AUTO_SHOW_ADVANCED: false,
    AUTO_EXPAND_MESSAGES: false,
    ENABLE_HELP_TOOLTIPS: true
}

// Initialize state from localStorage
const stored = localStorage.getItem(CONFIG_KEY)
const initialState = { ...defaultSettings }
if (stored) {
    try {
        const savedSettings = JSON.parse(stored)
        // Load supported settings only; obsolete preferences are ignored.
        for (const key of Object.keys(defaultSettings)) {
            if (typeof savedSettings?.[key] === 'boolean') {
                initialState[key] = savedSettings[key]
            }
        }
    } catch {
        // Use defaults if saved settings are malformed.
    }
}

export const configStore = reactive(initialState)

// Watch for changes and save to localStorage
watch(configStore, (newVal) => {
    localStorage.setItem(CONFIG_KEY, JSON.stringify(newVal))
}, { deep: true })
