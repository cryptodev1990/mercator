if [ -z "$DD_API_KEY" ]; then
    echo "Error: DD_API_KEY is required for DataDog Agent but was not set.  Exiting."
    exit 1
fi

sed -i "s/MY_DD_API_KEY_PLACEHOLDER/$DD_API_KEY/g" /etc/datadog-agent/datadog.yaml
service datadog-agent start || exit 0
service datadog-agent start
