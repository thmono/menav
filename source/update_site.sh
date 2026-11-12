#!/bin/bash
# 更新线上书签站：重新归类 → 构建 → 推送
# 用法： ./update_site.sh                  # 自动读 Chrome 账号云书签
#        ./update_site.sh 导出.html        # 用指定导出文件
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="${1:-}"
BUILD=/tmp/menav-test
PUB=/tmp/push-site

echo "① 按应用类型归类"
if [ -n "$SRC" ]; then
  python3 "$DIR/build_site.py" "$SRC" --top 15
else
  python3 "$DIR/build_site.py" --top 15
fi

echo "② 构建静态站"
if [ ! -d "$BUILD" ]; then
  git clone --depth 1 https://github.com/rbetree/menav.git "$BUILD"
  (cd "$BUILD" && npm ci --no-audit --no-fund)
fi
rm -rf "$BUILD/config/user"; mkdir -p "$BUILD/config/user/pages"
cp "$DIR/config/user/site.yml" "$BUILD/config/user/site.yml"
cp "$DIR/config/user/pages/bookmarks.yml" "$BUILD/config/user/pages/bookmarks.yml"
NODE_OK=$(node -e "const v=process.versions.node.split('.').map(Number);process.exit((v[0]>22||(v[0]===22&&(v[1]>23||(v[1]===23&&v[2]>=4))))?0:1)" 2>/dev/null && echo yes || echo no)
if [ "$NODE_OK" = "no" ]; then
  export PATH="$(dirname "$(npx -y node@22.23.4 -p 'process.execPath')"):$PATH"
  echo "   （已切到 $(node --version)）"
fi
(cd "$BUILD" && npm run build)

echo "③ 发布到 GitHub Pages"
rm -rf "$PUB"; mkdir -p "$PUB"
cp -R "$BUILD/dist"/. "$PUB"/
touch "$PUB/.nojekyll"
mkdir -p "$PUB/source/config/user/pages"
cp "$DIR/config/user/site.yml" "$PUB/source/config/user/site.yml"
cp "$DIR/config/user/pages/bookmarks.yml" "$PUB/source/config/user/pages/bookmarks.yml"
cp "$DIR/taxonomy.py" "$DIR/build_site.py" "$DIR/update_site.sh" "$PUB/source/" 2>/dev/null || true
cd "$PUB"
git init -q -b main
git add -A
git -c user.name=thmono -c user.email=thmono@users.noreply.github.com commit -q -m "同步书签 $(date '+%F %H:%M')（$(python3 -c "
import yaml;d=yaml.safe_load(open('$DIR/config/user/pages/bookmarks.yml'));
print(sum(len(c['sites']) for c in d['categories'][2:]),'个站点')" 2>/dev/null || echo '')）"
git remote add origin git@github.com:thmono/menav.git 2>/dev/null || git remote set-url origin git@github.com:thmono/menav.git
git push -f -q origin main
echo "✅ 已发布：https://thmono.github.io/menav/"
