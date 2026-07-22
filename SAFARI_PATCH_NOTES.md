# Safari Özel Filtreler yaması

Bu yama Chrome ve Firefox filtrelerini değiştirmez.

Eklenen çıktılar:

- `filters/dist/temizweb-main-safari.txt`
- `filters/dist/temizweb-pmo-safari.txt`
- `filters/dist/temizweb-social-safari.txt`

Safari çıktıları yalnızca somut alan adına bağlı kozmetik/prosedürel kuralları içerir.
Ağ/DNS kuralları, genel `*##` kuralları ve `#@#` istisnaları alınmaz.
Çok alan adlı kurallar her alan adına ayrı ayrı genişletilir ve `#?#` kuralları
Safari uBlock Origin Lite'ın gösterdiği `##` biçimine dönüştürülür.

`docs/install/index.html` içindeki Safari bölümü seçilen Safari çıktısını tek
seferde indirip panoya kopyalar. Chrome/Firefox abonelik ve URL akışları aynen kalır.

GitHub Actions mevcut `scripts/build_all.py` çalıştığında Safari çıktılarını da
otomatik üretir. Mevcut workflow zaten `filters/dist` klasörünü commit ettiği için
ek workflow değişikliği gerekmez.
