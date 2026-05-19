git clone https://github.com/jmojpar/gestor-tareas-api.git
cd gestor-tareas-api
git remote set-url origin https://github.com/dgarciap88/gestor-tareas-api.git
git remote add upstream https://github.com/jmojpar/gestor-tareas-api.git
git fetch upstream
git push origin main
git push origin refs/remotes/upstream/escenario-1-bug-logico:refs/heads/escenario-1-bug-logico
git push origin refs/remotes/upstream/escenario-2-sin-tests:refs/heads/escenario-2-sin-tests
git push origin refs/remotes/upstream/escenario-3-codigo-duplicado:refs/heads/escenario-3-codigo-duplicado
git push origin refs/remotes/upstream/escenario-4-sin-documentacion:refs/heads/escenario-4-sin-documentacion
git push origin refs/remotes/upstream/escenario-5-endpoint-roto:refs/heads/escenario-5-endpoint-roto