// 纯 JS 配置，避免从项目目录解析 vitest/config（vitest 由隔离环境提供）。
export default {
  test: {
    environment: "jsdom",
    include: ["tests/**/*.test.ts", "tests/**/*.test.tsx"],
  },
};
