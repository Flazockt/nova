param(
    [Parameter(Mandatory = $true)]
    [string]$VoiceToken
)

$ErrorActionPreference = "Stop"
$voice = $null
$token = $null
$pitchSteps = @(7, 2, 8, 3)

try {
    [Console]::InputEncoding = [System.Text.Encoding]::ASCII
    $voice = New-Object -ComObject SAPI.SpVoice
    $token = New-Object -ComObject SAPI.SpObjectToken
    $token.SetId($VoiceToken)
    $voice.Voice = $token
    $voice.Rate = 2

    while ($null -ne ($line = [Console]::In.ReadLine())) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }
        $separator = $line.IndexOf(":")
        if ($separator -lt 1) {
            continue
        }
        $sequence = $line.Substring(0, $separator)
        if ($sequence -notmatch '^\d+$') {
            continue
        }

        $text = [System.Text.Encoding]::UTF8.GetString(
            [Convert]::FromBase64String($line.Substring($separator + 1))
        )
        if (-not [string]::IsNullOrWhiteSpace($text)) {
            $chunks = [regex]::Matches($text, '\S+(?:\s+\S+){0,3}\s*')
            $markup = New-Object System.Text.StringBuilder
            for ($i = 0; $i -lt $chunks.Count; $i++) {
                $pitch = $pitchSteps[$i % $pitchSteps.Count]
                $chunk = [System.Security.SecurityElement]::Escape($chunks[$i].Value)
                [void]$markup.Append('<pitch absmiddle="' + $pitch + '">' + $chunk + '</pitch>')
                if ($i -lt $chunks.Count - 1) {
                    [void]$markup.Append('<silence msec="25"/>')
                }
            }
            $voice.Speak($markup.ToString(), 10) | Out-Null
            [Console]::Out.WriteLine("NOVA_DONE:" + $sequence)
            [Console]::Out.Flush()
        }
    }

    $voice.WaitUntilDone(10000) | Out-Null
}
catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
finally {
    if ($voice) {
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($voice)
    }
    if ($token) {
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($token)
    }
}
