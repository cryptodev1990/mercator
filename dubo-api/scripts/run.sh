__start_dd_agent() {
  if [ -z "$DD_API_KEY" ]; then
      echo "Error: DD_API_KEY is required for DataDog Agent but was not set.  Exiting."
      exit 1
  fi

  sed -n "s/MY_DD_API_KEY_PLACEHOLDER/$DD_API_KEY/g" /etc/datadog-agent/datadog.yaml
  service datadog-agent start
}

# if DD_ENABLED is true, then start the DataDog agent
if [ "$DD_ENABLED" = "true" ]
then
    __start_dd_agent
fi

uvicorn api.main:app --reload --host=0.0.0.0 --port=8080
