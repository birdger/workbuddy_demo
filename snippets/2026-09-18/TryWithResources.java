// 每日一技 demo：Java try-with-resources 自动资源管理
// 运行：javac TryWithResources.java && java TryWithResources
// （JDK 7+ 即可，本机 JDK 8 实测通过）

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class TryWithResources {

    /** 自定义资源：实现 AutoCloseable 就能放进 try(...) 小括号 */
    static class Timer implements AutoCloseable {
        private final long start = System.nanoTime();
        private final String name;

        Timer(String name) { this.name = name; }

        @Override
        public void close() {
            System.out.printf("  [%s] 关闭时耗时统计：%.3f ms%n",
                    name, (System.nanoTime() - start) / 1e6);
        }
    }

    public static void main(String[] args) throws IOException {
        // 1) 多资源 + 逆序关闭演示
        System.out.println("== try-with-resources：多资源逆序自动关闭 ==");
        try (Timer a = new Timer("资源A-先开");
             Timer b = new Timer("资源B-后开")) {
            System.out.println("  业务逻辑执行中……");
            Thread.sleep(50); // 模拟耗时
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        System.out.println("（可看到 B 先关、A 后关——与声明顺序相反）\n");

        // 2) 写文件再读回来：IO 资源全自动关闭
        System.out.println("== 写文件再读回，无需 finally ==");
        Path file = Paths.get("hello.txt");
        try (BufferedWriter w = Files.newBufferedWriter(file, StandardCharsets.UTF_8)) {
            w.write("try-with-resources 真好用");
            w.newLine();
            w.write("无需手写 finally 关流");
        }
        try (BufferedReader r = Files.newBufferedReader(file, StandardCharsets.UTF_8)) {
            String line;
            while ((line = r.readLine()) != null) {
                System.out.println("  读到: " + line);
            }
        }
        Files.deleteIfExists(file);

        // 3) 异常时依然会关闭：抑制异常（suppressed）演示
        System.out.println("\n== 异常路径下资源照样关闭 ==");
        try (Timer t = new Timer("异常资源")) {
            throw new IllegalStateException("业务代码炸了");
        } catch (IllegalStateException e) {
            System.out.println("  捕获到: " + e.getMessage());
        }
        System.out.println("\n要点：");
        System.out.println("1. AutoCloseable 接口的 close() 无异常版是 Closeable 的父接口");
        System.out.println("2. 资源按声明逆序关闭");
        System.out.println("3. try 块抛异常后 close() 也抛异常时，后者存为 suppressed");
    }
}
