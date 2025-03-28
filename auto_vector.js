const { exec } = require('child_process');

hexo.extend.filter.register('before_generate', function() {
  console.log("🎯 正在构建向量库...");

  return new Promise((resolve, reject) => {
    exec("D:/Personal_Project/HexoAgent/.venv/Scripts/python D:/Personal_Project/HexoAgent/build_vector_store.py",
      { cwd: "D:/Blog" },
      (err, stdout, stderr) => {
        if (err) {
          console.error("❌ 向量构建失败：", stderr);
          reject(err);
        } else {
          console.log("✅ 向量构建成功！");
          console.log(stdout);
          resolve();
        }
      }
    );
  });
});