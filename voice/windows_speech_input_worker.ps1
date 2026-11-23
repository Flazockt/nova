$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = New-Object -TypeName System.Text.UTF8Encoding -ArgumentList $false
$engine = $null

try {
    Add-Type -AssemblyName System.Speech
    $culture = [System.Globalization.CultureInfo]::GetCultureInfo("de-DE")
    $engine = New-Object -TypeName System.Speech.Recognition.SpeechRecognitionEngine `
        -ArgumentList $culture
    $engine.SetInputToDefaultAudioDevice()
    $grammar = New-Object -TypeName System.Speech.Recognition.DictationGrammar
    $engine.LoadGrammar($grammar)
    $engine.InitialSilenceTimeout = [TimeSpan]::FromSeconds(5)
    $engine.BabbleTimeout = [TimeSpan]::FromSeconds(3)
    $engine.EndSilenceTimeout = [TimeSpan]::FromSeconds(1)

    $result = $engine.Recognize([TimeSpan]::FromSeconds(60))
    if ($null -eq $result -or [string]::IsNullOrWhiteSpace($result.Text)) {
        [Console]::Error.WriteLine("Keine Sprache erkannt.")
        exit 2
    }

    [Console]::Out.WriteLine($result.Text)
}
catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
finally {
    if ($engine) {
        $engine.Dispose()
    }
}
