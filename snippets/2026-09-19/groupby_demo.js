/**
 * 每日一技 demo · 2026-09-19
 * 主题：ES2024 Object.groupBy / Map.groupBy —— 一行搞定数组分组
 *
 * 运行方式：
 *   node groupby_demo.js        （需要 Node.js >= 21）
 */

const repos = [
  { name: "fzf", lang: "Go", stars: 81000 },
  { name: "bat", lang: "Rust", stars: 59300 },
  { name: "rich", lang: "Python", stars: 57400 },
  { name: "ripgrep", lang: "Rust", stars: 65100 },
  { name: "httpie", lang: "Python", stars: 37300 },
  { name: "starship", lang: "Rust", stars: 58300 },
];

// 1. Object.groupBy：键为字符串的普通对象
const byLang = Object.groupBy(repos, (r) => r.lang);
console.log("== 按语言分组 ==");
for (const [lang, list] of Object.entries(byLang)) {
  console.log(`${lang}: ${list.map((r) => r.name).join(", ")}`);
}

// 2. 分组 + 聚合：每组的 star 总数
console.log("\n== 各语言 star 总数 ==");
for (const [lang, list] of Object.entries(byLang)) {
  const total = list.reduce((sum, r) => sum + r.stars, 0);
  console.log(`${lang}: ${total.toLocaleString()} ⭐`);
}

// 3. Map.groupBy：键可以是任意类型（这里用数字区间对象不行，用布尔/数值演示）
const bySize = Map.groupBy(repos, (r) => (r.stars >= 60000 ? "🔥 6万+" : "⭐ 6万以下"));
console.log("\n== 按热度分组（Map，键可以是任意类型） ==");
for (const [bucket, list] of bySize) {
  console.log(`${bucket}: ${list.map((r) => r.name).join(", ")}`);
}
