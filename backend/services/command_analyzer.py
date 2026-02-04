import re
from typing import Dict, List, Tuple

class CommandAnalyzer:
    
    def __init__(self):
        # Dangerous command patterns
        self.dangerous_patterns = {
            'rm -rf': {'risk': 'critical', 'description': 'Recursive file deletion - catastrophic data loss'},
            'rm ': {'risk': 'high', 'description': 'File deletion command - can cause data loss'},
            'dd': {'risk': 'high', 'description': 'Direct disk write - can destroy entire system'},
            'dd if=': {'risk': 'high', 'description': 'Direct disk write with input file - dangerous disk overwrite'},
            'shred': {'risk': 'high', 'description': 'Secure delete - can irreversibly destroy data'},
            'mkfs': {'risk': 'critical', 'description': 'Format filesystem - complete data destruction'},
            'format': {'risk': 'critical', 'description': 'Disk formatting command (Windows/Linux) - data loss'},
            'cipher /w': {'risk': 'high', 'description': 'Wipes free space on Windows - destructive'},
            'del /f /q': {'risk': 'high', 'description': 'Force delete files on Windows - data loss'},
            'rd /s /q': {'risk': 'high', 'description': 'Remove directory tree on Windows - data loss'},
            'mkfs.': {'risk': 'critical', 'description': 'Filesystem creation utility - destructive'},
            'mount': {'risk': 'medium', 'description': 'Mount filesystem - system modification'},
            'losetup': {'risk': 'medium', 'description': 'Attach disk images - can modify block devices'},
            'chmod 777': {'risk': 'medium', 'description': 'Makes files world-writable - security risk'},
            'chmod 000': {'risk': 'medium', 'description': 'Removes all permissions - may break access'},
            'chown -R': {'risk': 'medium', 'description': 'Recursive ownership change - can lock or expose files'},
            'chown': {'risk': 'medium', 'description': 'Ownership change - can lock out users'},
            'useradd': {'risk': 'medium', 'description': 'Creates system user - could add backdoor accounts'},
            'adduser': {'risk': 'medium', 'description': 'Creates system user - could add backdoor accounts'},
            'groupadd': {'risk': 'medium', 'description': 'Creates group accounts - permission changes'},
            'passwd': {'risk': 'medium', 'description': 'Password change - may lock/unlock accounts'},
            'sudo': {'risk': 'high', 'description': 'Superuser execution - elevated privileges'},
            'su -': {'risk': 'high', 'description': 'Switch user to root - elevated privileges'},
            'killall': {'risk': 'medium', 'description': 'Force kill processes - can crash system'},
            'pkill': {'risk': 'medium', 'description': 'Kill processes by name - can stop critical services'},
            'iptables -F': {'risk': 'high', 'description': 'Flush firewall rules - may expose system'},
            'ufw disable': {'risk': 'high', 'description': 'Disable firewall - reduces protection'},
            'systemctl disable': {'risk': 'high', 'description': 'Disable system service - can break system'},
            'systemctl stop': {'risk': 'high', 'description': 'Stop system service - may interrupt operations'},
            'reboot': {'risk': 'medium', 'description': 'Reboot system - disruptive'},
            'shutdown': {'risk': 'medium', 'description': 'Shutdown system - disruptive'},
            'poweroff': {'risk': 'medium', 'description': 'Power off system - disruptive'},
            'init 0': {'risk': 'high', 'description': 'Switch to runlevel 0 - shutdown equivalent'},
            'halt': {'risk': 'high', 'description': 'Halt system - disruptive'},
            'telinit 0': {'risk': 'high', 'description': 'Change runlevel to 0 - disruptive'},
            ':(){:|:&};:': {'risk': 'critical', 'description': 'Fork bomb - system crash attack'},
            'curl | bash': {'risk': 'high', 'description': 'Remote script piped to shell - remote code execution'},
            'wget | bash': {'risk': 'high', 'description': 'Remote script piped to shell - remote code execution'},
            'powershell -enc': {'risk': 'high', 'description': 'Encoded PowerShell command - potential obfuscated payload'},
            'powershell -command': {'risk': 'high', 'description': 'PowerShell execution - can perform system changes'},
            'certutil -decode': {'risk': 'high', 'description': 'Decode files with Windows certutil - used to drop payloads'},
            'certutil -decodehex': {'risk': 'high', 'description': 'Decode hex payloads - used to drop payloads'},
        }

        # Suspicious regex patterns
        self.suspicious_patterns = {
            r'(?:\|\s*nc\s+|>\s*/dev/tcp/)': 'Reverse shell attempt',
            r'(?:bash\s+-i|sh\s+-i)': 'Interactive shell spawning',
            r'(?:curl|wget)\s+[^|]*(?:\||-O\s*-).*?(?:bash|sh|python|perl|php)': 'Remote code execution via pipe or download',
            r'(?:`.*`|\$\(.*\))': 'Command substitution - code injection risk',
            r'bash\s+-c\s+".*nc\s"': 'Command spawning network utility via bash - possible reverse shell',
            r'python\s+-c\s+".*socket|subprocess.*"': 'Python one-liner launching sockets/subprocess - potential remote shell',
            r'perl\s+-e': 'Perl one-liner - often used for compact reverse shells',
            r'php\s+-r': 'PHP one-liner - may execute remote code',
            r'ruby\s+-e': 'Ruby one-liner - may execute remote code',
            r'socat\s+TCP': 'socat network transfer - may be used for remote shells',
            r'openssl\s+s_client\s+-connect': 'Openssl client connecting - can be used for exfiltration or shell',
            r'\b(eval|exec)\b\s*\(': 'Eval/exec usage - code execution risk',
            r'base64\s+-d': 'Base64 decode - often used to unwrap payloads',
            r'certutil\s+-decode': 'Windows certutil decode - used to drop payloads',
            r'powershell\s+-enc': 'Encoded PowerShell - obfuscated commands',
            r'powershell\s+-command': 'PowerShell execution - sensitive on Windows',
            r'2>\s*/dev/null': 'Error suppression - hiding errors',
            r'>\s*/dev/null': 'Output suppression - hiding activity',
            r'\b\$\([^\)]*\)': 'Command substitution - injection risk',
            r'\b`[^`]+`': 'Backtick substitution - injection risk',
            r'\b(eval|xargs)\b': 'Eval/xargs usage - may chain dangerous commands',
            r'&\s*$': 'Background execution - hidden process',
            r';\s*$': 'Command chaining - multiple operations',
            r'\bopenssl\b.*\brand\b': 'OpenSSL randomness commands - unusual use may indicate obfuscation',
            r'certutil\s+-urlcache\s+-split': 'Certutil URL cache usage - potential payload retrieval',
            r'curl\s+.*\|\s*sh': 'curl piped to sh - remote code execution',
            r'wget\s+.*\|\s*sh': 'wget piped to sh - remote code execution',
            r'\b(powershell|pwsh)\b.*-nop': 'PowerShell with -NoProfile/-NonInteractive - often used in attacks',
        }
        
        # Safe commands
        self.safe_commands = {
            'ls', 'cd', 'pwd', 'cat', 'echo', 'grep', 'find', 'cp', 'mkdir',
            'mv', 'touch', 'tail', 'head', 'wc', 'sort', 'uniq', 'diff',
            'cal', 'date', 'whoami', 'hostname', 'man', 'help', 'history'
        }

    def analyze_command(self, command: str) -> Dict:
        command = command.strip()
        
        if not command:
            return {
                'prediction': 'safe',
                'risk_level': 'none',
                'confidence': 100.0,
                'message': 'Empty command - no risk detected',
                'details': []
            }
        
        risk_level = 'safe'
        confidence = 100.0
        details = []
        risk_score = 0
        
        # Check for dangerous commands
        for danger_cmd, danger_info in self.dangerous_patterns.items():
            if danger_cmd in command.lower():
                risk_level = 'dangerous'
                confidence = max(confidence - 10, 50)
                risk_score += 3
                details.append({
                    'type': 'dangerous_command',
                    'pattern': danger_cmd,
                    'risk': danger_info['risk'],
                    'description': danger_info['description']
                })
        
        # Check for suspicious patterns
        for pattern, description in self.suspicious_patterns.items():
            if re.search(pattern, command, re.IGNORECASE):
                risk_level = 'suspicious'
                confidence = max(confidence - 15, 40)
                risk_score += 2
                details.append({
                    'type': 'suspicious_pattern',
                    'pattern': pattern,
                    'description': description
                })
        
        # Check for encoded commands
        if any(keyword in command.lower() for keyword in ['base64', 'encoded', 'hex', 'rot13']):
            risk_level = 'suspicious'
            confidence = max(confidence - 10, 50)
            risk_score += 1.5
            details.append({
                'type': 'encoding_detected',
                'pattern': 'Command encoding',
                'description': 'Encoded commands may hide malicious intent'
            })
        
        
        main_command = command.split()[0].split('/')[-1].lower()
        if main_command in self.safe_commands:
            if not details:
                risk_level = 'safe'
                confidence = 95.0
                details.append({
                    'type': 'safe_command',
                    'pattern': main_command,
                    'description': 'Common safe utility command'
                })
        
        # Calculate final confidence
        if risk_score > 0:
            confidence = max(50 - (risk_score * 10), 10)
        

        is_safe = risk_level == 'safe'
        
        return {
            'prediction': 'safe' if is_safe else 'dangerous',
            'risk_level': risk_level,
            'confidence': confidence,
            'message': self._get_risk_message(risk_level, is_safe),
            'details': details,
            'risk_score': risk_score,
            'main_command': main_command
        }
    
    def _get_risk_message(self, risk_level: str, is_safe: bool) -> str:
    #Generate the user-friendly message
        messages = {
            'safe': 'This command appears to be safe to execute.',
            'dangerous': 'WARNING: This command contains dangerous operations. Exercise caution!',
            'suspicious': 'CAUTION: This command shows suspicious patterns. Verify before execution.',
            'critical': 'CRITICAL: This command appears to be a malicious attack. Do NOT execute!'
        }
        return messages.get(risk_level, 'Unable to determine risk level.')


analyzer = CommandAnalyzer()

def analyze_terminal_command(command: str) -> Dict:
    return analyzer.analyze_command(command)
