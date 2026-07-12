# TemizWeb Clean Ultimate

Tek ve çakışmasız GitHub Actions workflow'u hem uBlock hem DNS çıktılarını üretir.

## İlk kurulum

1. `TemizWeb` adlı boş ve **Public** bir GitHub deposu oluşturun.
2. Bu ZIP'in içindeki dosyaları depo köküne yükleyin.
3. **Settings → Actions → General → Workflow permissions → Read and write permissions** seçin.
4. **Actions → Build TemizWeb → Run workflow** çalıştırın.
5. Tek workflow başarılı olunca `filters/dist` ve `dns/dist` güncellenir.
6. GitHub Pages için **Settings → Pages → Deploy from a branch → main /docs** seçin.

## uBlock bağlantısı

`https://raw.githubusercontent.com/neverfap-akademi/TemizWeb/main/filters/dist/temizweb-main.txt`

## Neden tek workflow?

Önceki iki workflow aynı anda `main` dalına commit atarak push çakışması çıkarabiliyordu. Bu depoda yalnızca `.github/workflows/build.yml` vardır ve bütün çıktılar tek commit ile güncellenir.

## Çıktılar

- `filters/dist/temizweb-main.txt`
- `dns/dist/temizweb-balanced-*`
- `dns/dist/temizweb-strict-*`

Balanced yalnızca yetişkin alan adlarını; Strict ayrıca seçilmiş VPN/proxy sitelerini içerir. Hiçbiri SafeSearch yönlendirmesi yapmaz.
