import { defineConfig } from "allure";

export default defineConfig({
  name: "TestFlow PyTest",
  output: "./allure-report",
  historyPath: "./allure-history/history.jsonl",
  plugins: {
    awesome: {
      options: {
        reportName: "TestFlow PyTest",
        reportLanguage: "pt",
        singleFile: false,
        open: false,
      },
    },
  },
});
