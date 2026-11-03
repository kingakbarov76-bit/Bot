# Zaxira joylash (konteyner)

Asosiy tizim Supabase'da ishlaydi (bepul, 24/7). Server muammo qilsa, shu konteynerlar bir xil bazaga ulanib ishlaydi.

1. `cp .env.example .env` va 3 ta qiymatni to'ldiring (kalitlar Supabase Settings → API; POSTER_CRON_KEY jadvaldagi bot_config'da).
2. `docker compose up -d`
3. Mijoz boti webhook'ini o'zgartirish kerak bo'lsa: Telegram setWebhook url=https://<sizning-domen>/ (8001-port). Qa uchun 8002.
4. Supabase pg_cron o'chirilgan bo'lsagina `cron` xizmatini yoqing, aks holda postlar ikki baravar chiqadi.

Eslatma: botlar tokeni bazadagi bot_config jadvalidan o'qiladi, shuning uchun konteynerga qo'shimcha sir kerak emas.
Funksiyalarni Supabase'ga qayta joylash: `supabase functions deploy <nom> --no-verify-jwt`.
