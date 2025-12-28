// 这个文件用于验证环境变量是否正确配置
// 开发时使用，生产时可以删除

console.log('API Key 配置状态:');
console.log('NEXT_PUBLIC_GOOGLE_MAPS_API_KEY:', 
  process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ? '✅ 已配置' : '❌ 未配置');

if (!process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY) {
  console.warn('⚠️ 警告: Google Maps API 密钥未配置');
  console.warn('请确保 .env.local 文件存在并包含有效的 API 密钥');
}
