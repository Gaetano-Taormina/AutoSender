import { spawn } from 'child_process';

console.log("[INFO] Avvio dell'orchestratore Node.js...");

const pythonExecutable = './.venv/Scripts/python.exe';
const pythonScript = 'src/backend/main.py';

const child = spawn(pythonExecutable, ['-u', pythonScript]);

child.stdout.on('data', (data) => process.stdout.write(`[PYTHON LOG]: ${data}`));
child.stderr.on('data', (data) => process.stderr.write(`[PYTHON ERROR]: ${data}`));
child.on('close', (code) => console.log(`[PYTHON EXIT]: Codice ${code}`));

const killChild = () => {
  if (!child.killed) {
    console.log("[INFO] Spegnimento del processo Node rilevato. Terminazione del processo Python in corso...");
    child.kill('SIGINT');
  }
};

process.on('exit', killChild);
process.on('SIGINT', () => { killChild(); process.exit(); });
process.on('SIGTERM', () => { killChild(); process.exit(); });
process.on('uncaughtException', (err) => {
  console.error("[ERROR] Crash critico di Node.js. Chiusura emergenza...", err);
  killChild();
  process.exit(1);
});
