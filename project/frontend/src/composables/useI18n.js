import { ref, computed } from "vue";
import { getLocale, setLocale, messages } from "../locales/index.js";

const currentLocale = ref(getLocale());

function translate(key, params = {}, locale = currentLocale.value) {
  const keys = key.split(".");
  let value = messages[locale];
  
  for (const k of keys) {
    if (value && value[k]) {
      value = value[k];
    } else {
      return key;
    }
  }
  
  if (typeof value === "string") {
    return value.replace(/\{(\w+)\}/g, (_, k) => params[k] || "");
  }
  
  return key;
}

export function useI18n() {
  const locale = computed(() => currentLocale.value);

  function t(key, params = {}) {
    return translate(key, params, currentLocale.value);
  }

  function changeLocale(newLocale) {
    setLocale(newLocale);
    currentLocale.value = newLocale;
  }

  return {
    locale,
    t,
    changeLocale,
  };
}
