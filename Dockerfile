# Zaxira konteyner: Supabase Edge funksiyalarini istalgan serverda ishga tushiradi.
# Ishlatish: docker build -t aipm . && docker run -e FN=poster -e SUPABASE_URL=... -e SUPABASE_SERVICE_ROLE_KEY=... -p 8000:8000 aipm
FROM denoland/deno:2.1.4
WORKDIR /app
COPY supabase/functions ./functions
ENV FN=bot DENO_SERVE_ADDRESS=tcp:0.0.0.0:8000
EXPOSE 8000
CMD ["sh","-c","deno run -A functions/$FN/index.ts"]
