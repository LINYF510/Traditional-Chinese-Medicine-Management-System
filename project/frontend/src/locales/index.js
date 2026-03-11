import zhCN from "./zh-CN.js";
import enUS from "./en-US.js";

const messages = {
  "zh-CN": zhCN,
  "en-US": enUS,
};

let currentLocale = localStorage.getItem("locale") || "zh-CN";

function setLocale(locale) {
  if (messages[locale]) {
    currentLocale = locale;
    localStorage.setItem("locale", locale);
    document.documentElement.lang = locale;
  }
}

function getLocale() {
  return currentLocale;
}

export { messages, setLocale, getLocale };
