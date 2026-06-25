# 🚀 SCOUT PRO — Guía para crear el Ejecutable

## Archivos que necesitás
```
📁 tu-carpeta/
├── app.py           ← tu aplicación Scout Pro
├── launcher.py      ← arrancador del ejecutable
└── scout_pro.spec   ← configuración de PyInstaller
```

---

## PASO 1 — Instalar Python
Si no tenés Python instalado:
👉 https://www.python.org/downloads/
- Descargá la versión **3.11** (la más compatible)
- Al instalar, **tildá "Add Python to PATH"** ✅

---

## PASO 2 — Instalar las dependencias

Abrí **CMD** o **PowerShell** en la carpeta del proyecto y ejecutá:

```bash
pip install streamlit plotly matplotlib numpy fpdf2 pyinstaller
```

Esperá que termine (puede tardar unos minutos).

---

## PASO 3 — Construir el ejecutable

En la misma carpeta, ejecutá:

```bash
pyinstaller scout_pro.spec
```

Esto tarda **3-10 minutos**. Vas a ver muchos mensajes, es normal.

---

## PASO 4 — Encontrar tu ejecutable

Cuando termine, vas a ver una carpeta nueva llamada `dist/`:

```
📁 dist/
└── 📁 ScoutPro/
    ├── ScoutPro.exe     ← ¡Este es tu ejecutable!
    └── (muchos archivos de soporte)
```

---

## PASO 5 — Distribuir

Para compartir la app con alguien:
- **Comprimí toda la carpeta** `dist/ScoutPro/` en un ZIP
- La otra persona descomprime y hace doble clic en `ScoutPro.exe`
- Se abre el navegador automáticamente con la app ✅
- No necesita tener Python instalado

---

## ⚠️ Notas importantes

- **Windows Defender** puede dar una advertencia la primera vez (es normal para ejecutables nuevos). Hacé clic en "Más información" → "Ejecutar de todas formas".
- El ejecutable **solo funciona en Windows**. Para Mac o Linux hay que compilar en esa plataforma.
- La carpeta `ScoutPro/` completa es necesaria, no solo el `.exe`.

---

## 🎯 Alternativa más simple — BAT launcher

Si no querés el ejecutable compilado y solo necesitás que sea fácil de abrir, creá un archivo `ScoutPro.bat` con este contenido:

```bat
@echo off
title SCOUT PRO
echo Iniciando Scout Pro...
start "" http://localhost:8501
streamlit run app.py --server.headless true --browser.gatherUsageStats false
```

Hacé doble clic en el `.bat` y listo. Requiere Python instalado pero es instantáneo.

---

## 🆘 Problemas comunes

| Error | Solución |
|-------|----------|
| `streamlit no reconocido` | Reinstalá con `pip install streamlit` |
| `ModuleNotFoundError` | Agregá el módulo a `hiddenimports` en el .spec |
| La ventana se cierra sola | Revisá que `console=True` en el .spec para ver el error |
| Puerto 8501 ocupado | Cambiá el puerto en launcher.py a `8502` |
