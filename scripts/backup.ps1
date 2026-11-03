$raizProyecto = Split-Path -Parent $PSScriptRoot
Set-Location $raizProyecto

# Configurar el archivo de registro
$directorioLogs = "./backups/logs"

New-Item -ItemType Directory -Force -Path $directorioLogs | Out-Null

$archivoLog = Join-Path $directorioLogs "backup.log"

# Escribir un mensaje en el registro
function Write-Log {
    param(
        [string]$Nivel,
        [string]$Mensaje
    )

    $fechaLog = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    Add-Content -LiteralPath $archivoLog -Value "[$fechaLog] $Nivel - $Mensaje" -Encoding UTF8 -ErrorAction Stop
}

# Impedir ejecuciones simultáneas
$directorioBloqueo = "./backups"
New-Item -ItemType Directory -Force -Path $directorioBloqueo | Out-Null

$rutaBloqueo = Join-Path $directorioBloqueo "backup.lock"

try {
    $bloqueo = [System.IO.File]::Open(
        (Join-Path (Get-Location).Path $rutaBloqueo),
        [System.IO.FileMode]::OpenOrCreate,
        [System.IO.FileAccess]::ReadWrite,
        [System.IO.FileShare]::None
    )
}
catch [System.IO.IOException] {
    Write-Warning "Ya hay otra ejecución del backup en curso."
    exit 1
}
try {
    $inicioBackup = Get-Date

    Write-Log -Nivel "INFO" -Mensaje "Iniciando proceso de backup"

    # 1. Generar el nombre del backup con fecha y hora
    $fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $archivo = "perfumes_store_$fecha.backup"

    # 2. Definir y crear los directorios necesarios
    $directorio = "./backups/daily"

    New-Item -ItemType Directory -Force -Path $directorio, "./backups/weekly", "./backups/monthly" | Out-Null

    # 3. Generar el backup dentro del contenedor PostgreSQL
    $proceso = New-Object System.Diagnostics.Process

    try {
        $proceso.StartInfo.FileName = "docker.exe"
        $proceso.StartInfo.Arguments = "compose -f compose.prod.yaml exec -T -u postgres db pg_dump -U perfumes_prod -d perfumes_store_prod -Fc -f /tmp/$archivo"

        $proceso.StartInfo.UseShellExecute = $false
        $proceso.StartInfo.RedirectStandardError = $true
        $proceso.StartInfo.CreateNoWindow = $true
        $proceso.StartInfo.WorkingDirectory = (Get-Location).Path

        $null = $proceso.Start()

        $detalleError = $proceso.StandardError.ReadToEnd()

        $proceso.WaitForExit()
        $codigoSalida = $proceso.ExitCode

        if ($codigoSalida -ne 0) {
            throw "Error al generar el backup (codigo $codigoSalida): $detalleError"
        }
    }
    finally {
        $proceso.Dispose()
    }

    # 4. Copiar el backup al ordenador
    # Copiar primero a un archivo temporal en Windows
    $archivoDiario = "$directorio/$archivo"
    $archivoTemporalDiario = "$archivoDiario.tmp"

    try {
    # Eliminar un posible temporal anterior
        if (Test-Path -LiteralPath $archivoTemporalDiario) {
            Remove-Item -LiteralPath $archivoTemporalDiario -ErrorAction Stop
        }

        # Copiar desde PostgreSQL al archivo temporal
        docker compose -f compose.prod.yaml cp "db:/tmp/$archivo" "$archivoTemporalDiario"

        if ($LASTEXITCODE -ne 0) {
            throw "Error al copiar el backup diario"
        }
    }
    catch {
        # Eliminar cualquier copia incompleta
        if (Test-Path -LiteralPath $archivoTemporalDiario) {
            Remove-Item -LiteralPath $archivoTemporalDiario -ErrorAction Stop
        }

        throw "Error durante la copia diaria: $_"
    }

    # Verificar el backup temporal antes de guardarlo definitivamente
    try {
        # Copiar el archivo temporal de Windows al contenedor
        docker compose -f compose.prod.yaml cp "$archivoTemporalDiario" "db:/tmp/verificar_$archivo"

        if ($LASTEXITCODE -ne 0) {
            throw "No se pudo copiar el backup para verificarlo"
        }

        # Comprobar que PostgreSQL puede leer el backup
        docker compose -f compose.prod.yaml exec -T db pg_restore --list "/tmp/verificar_$archivo" | Out-Null

        if ($LASTEXITCODE -ne 0) {
            throw "El backup no ha superado la verificacion"
        }

        # Convertir el temporal en un backup definitivo
        Move-Item -LiteralPath $archivoTemporalDiario -Destination $archivoDiario -ErrorAction Stop

        Write-Host "Backup diario verificado y guardado correctamente"
    }
    catch {
        # Descartar el archivo temporal si falla la verificacion
        if (Test-Path -LiteralPath $archivoTemporalDiario) {
            Remove-Item -LiteralPath $archivoTemporalDiario -ErrorAction Stop
        }

        throw "Error al verificar el backup diario: $_"
    }

    # 5. Calcular el año y la semana ISO
    $fechaActual = Get-Date

    $calendario = [System.Globalization.CultureInfo]::InvariantCulture.Calendar

    $diaSemana = ([int]$fechaActual.DayOfWeek + 6) % 7
    $jueves = $fechaActual.AddDays(3 - $diaSemana)

    $anioISO = $jueves.Year

    $semanaISO = $calendario.GetWeekOfYear(
        $jueves,
        [System.Globalization.CalendarWeekRule]::FirstFourDayWeek,
        [System.DayOfWeek]::Monday
    )

    $periodoSemanal = "{0}-W{1:D2}" -f $anioISO, $semanaISO

    # 6. Crear la copia semanal si todavía no existe
    $archivoSemanal = "./backups/weekly/perfumes_store_$periodoSemanal.backup"

    if (-not (Test-Path $archivoSemanal)) {
        $archivoTemporal = "$archivoSemanal.tmp"

        try {
            if (Test-Path -LiteralPath $archivoTemporal) {
            Remove-Item -LiteralPath $archivoTemporal -ErrorAction Stop
            Write-Host "Archivo temporal semanal anterior eliminado"
            }
            Copy-Item -Path "$directorio/$archivo" -Destination $archivoTemporal -ErrorAction Stop
            Move-Item -Path $archivoTemporal -Destination $archivoSemanal -ErrorAction Stop

            Write-Host "Backup semanal creado: $archivoSemanal"
        }
        catch {
            throw "Error al crear el backup semanal: $_"
        }
    }

    # 7. Crear la copia mensual si todavía no existe
    $periodoMensual = Get-Date -Format "yyyy-MM"
    $archivoMensual = "./backups/monthly/perfumes_store_$periodoMensual.backup"

    if (-not (Test-Path $archivoMensual)) {
        $archivoTemporal = "$archivoMensual.tmp"

        try {
            if (Test-Path -LiteralPath $archivoTemporal) {
            Remove-Item -LiteralPath $archivoTemporal -ErrorAction Stop
            Write-Host "Archivo temporal mensual anterior eliminado"
            }
            Copy-Item -Path "$directorio/$archivo" -Destination $archivoTemporal -ErrorAction Stop
            Move-Item -Path $archivoTemporal -Destination $archivoMensual -ErrorAction Stop

            Write-Host "Backup mensual creado: $archivoMensual"
        }
        catch {
            throw "Error al crear el backup mensual: $_"
        }
    }

    # 8. Confirmar la creación del backup diario
    Write-Host "Backup diario creado: $directorio/$archivo"


    # Obtener los backups diarios ordenados del más reciente al más antiguo
    $backups = @(
        Get-ChildItem -Path "./backups/daily" -Filter "*.backup" -File |
            Sort-Object LastWriteTime -Descending
    )

    $fechaLimite = (Get-Date).AddDays(-7)

    if ($backups.Count -gt 0) {
        $backupProtegido = $backups[0]

        Write-Host "Backup protegido: $($backupProtegido.Name)"

        foreach ($backup in $backups) {
            if ($backup.FullName -ne $backupProtegido.FullName -and
                $backup.LastWriteTime -lt $fechaLimite) {

                try {
                    Remove-Item -LiteralPath $backup.FullName -ErrorAction Stop
                    Write-Host "Backup diaria eliminada: $($backup.Name)"
                }
                catch {
                    Write-Warning "No se pudo eliminar el backup $($backup.Name): $_"
                }
            }
        }
    }

    # Conservar los 4 backups semanales más recientes
    $backupsSemanales = @(
        Get-ChildItem -Path "./backups/weekly" -Filter "*.backup" -File |
            Sort-Object LastWriteTime -Descending
    )

    for ($i = 4; $i -lt $backupsSemanales.Count; $i++) {
        $backup = $backupsSemanales[$i]

        try {
            Remove-Item -LiteralPath $backup.FullName -ErrorAction Stop
            Write-Host "Backup semanal eliminada: $($backup.Name)"
        }
        catch {
            Write-Warning "No se pudo eliminar el backup semanal $($backup.Name): $_"
        }
    }

    # Conservar los 3 backups mensuales más recientes
    $backupsMensuales = @(
        Get-ChildItem -Path "./backups/monthly" -Filter "*.backup" -File |
            Sort-Object LastWriteTime -Descending
    )

    for ($i = 3; $i -lt $backupsMensuales.Count; $i++) {
        $backup = $backupsMensuales[$i]

        try {
            Remove-Item -LiteralPath $backup.FullName -ErrorAction Stop
            Write-Host "Backup mensual eliminada: $($backup.Name)"
        }
        catch {
            Write-Warning "No se pudo eliminar el backup mensual $($backup.Name): $_"
        }
    }
    $duracion = (Get-Date) - $inicioBackup
    $segundos = [math]::Round($duracion.TotalSeconds, 2)
    Write-Log -Nivel "INFO" -Mensaje "Backup completado correctamente: $archivo (duracion: $segundos segundos)"

}

catch {
    $mensajeError = "El proceso de backup ha fallado: $_"

    Write-Host "ERROR: $mensajeError" -ForegroundColor Red

    # Registrar el error del backup
    try {
        Write-Log -Nivel "ERROR" -Mensaje $mensajeError
    }
    catch {
        Write-Warning "No se pudo escribir el error en el archivo de log: $_"
    }

    # Intentar enviar una alerta por correo
    try {
        $directorioCredenciales = Join-Path $env:APPDATA "PerfumesStore"

        $rutaCredencial = Join-Path $directorioCredenciales "gmail-password.txt"
        $rutaCorreo = Join-Path $directorioCredenciales "gmail-address.txt"

        $claveSegura = Get-Content $rutaCredencial -ErrorAction Stop |
            ConvertTo-SecureString -ErrorAction Stop

        $correoGmail = (Get-Content $rutaCorreo -Raw -ErrorAction Stop).Trim()

        $credencialGmail = [System.Management.Automation.PSCredential]::new(
            $correoGmail,
            $claveSegura
        )

        $datosAlerta = @{
            correo = $correoGmail
            password = $credencialGmail.GetNetworkCredential().Password
            error = $mensajeError
            fecha = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }

        $jsonAlerta = $datosAlerta | ConvertTo-Json -Compress

        $rutaPython = Join-Path $raizProyecto ".venv\Scripts\python.exe"
        $rutaScriptAlerta = Join-Path $raizProyecto "scripts\enviar_alerta.py"

        $jsonAlerta | & $rutaPython $rutaScriptAlerta

        if ($LASTEXITCODE -ne 0) {
            throw "El script de alertas ha fallado con codigo $LASTEXITCODE"
        }

        Write-Host "Alerta enviada correctamente" -ForegroundColor Green
    }
    catch {
        Write-Warning "No se pudo enviar la alerta por correo: $_"

        try {
            Write-Log -Nivel "ERROR" -Mensaje "No se pudo enviar la alerta: $_"
        }
        catch {
            Write-Warning "Tampoco se pudo registrar el fallo del correo: $_"
        }
    }
    finally {
        Remove-Variable jsonAlerta, datosAlerta, credencialGmail, claveSegura -ErrorAction SilentlyContinue
    }

    exit 1
}
finally {
    try {
        if ($archivo) {
            docker compose -f compose.prod.yaml exec -T db rm -f "/tmp/$archivo" "/tmp/verificar_$archivo"

            if ($LASTEXITCODE -ne 0) {
                Write-Warning "No se pudieron limpiar todos los temporales del contenedor"
            }
        }
    }
    catch {
        Write-Warning "Error durante la limpieza de temporales: $_"
    }
    finally {
        if ($null -ne $bloqueo) {
            $bloqueo.Dispose()
        }
    }
}
