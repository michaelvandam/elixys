from elixysweb import app
import logging.config
import logging
logging.config.fileConfig("elixysweb/config/elixyslog.conf")

log = logging.getLogger("elixys.web")
log.info("Starting Elixys Web Server")
app.run(debug=True,host='0.0.0.0')
