#!/bin/sh
# Oddiy rejalashtiruvchi: har daqiqa vaqtni tekshirib, funksiyalarni chaqiradi (UTC, pg_cron bilan bir xil jadval).
# Supabase pg_cron ishlayotgan bo'lsa, bu konteynerni YOQMANG (ikki marta post chiqib ketadi).
call() { curl -s -m 120 -H "x-cron-key: $POSTER_CRON_KEY" ${2:+-H "x-mode: $2"} "http://$1:8000/" -o /dev/null; }
while true; do
  H=$(date -u +%H); M=$(date -u +%M)
  case "$H" in 03|08|14) case "$M" in 00|10|20|30) call poster;; esac;; esac
  case "$H$M" in 0530|0730|0930|1130|1330|1530) call teaser;; esac
  case "$H$M" in 0550|1050|1650) call watchdog;; esac
  case "$M" in 20) [ $((10#$H % 3)) -eq 0 ] && call poster backfill;; esac
  sleep 60
done
