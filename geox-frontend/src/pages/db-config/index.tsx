import { useAuth0 } from "@auth0/auth0-react";
import { useEffect, useState } from "react";
import { FaSnowflake } from "react-icons/fa";
import { SiPostgresql } from "react-icons/si";
import { TbHeartPlus, TbTrash } from "react-icons/tb";
import {
  DbConfigService,
  Organization,
  OrganizationsService,
  PublicDbCredential,
} from "../../client";
import { Navbar } from "../../common/components/navbar";
import { useTokenInOpenApi } from "../../hooks/use-token-in-openapi";

const _placeholder = (text: string) => {
  switch (text) {
    case "display_name":
      return "Human-readable name, e.g. Analytics DB";
    case "database_user":
      return "DB bot user, e.g. mercator_geofencer_user";
    case "host":
      return "DB host address, e.g. 8.8.8.8 (example)";
    case "port":
      return "DB port, e.g. 5432";
    case "database":
      return "DB to operate in, e.g. main_db";
    case "extras":
      return 'e.g. {"ssl": true, "schema": "public"}';
  }
};

const DbConnectionModal = ({ hidden, setHidden }: any) => {
  if (hidden) {
    return null;
  }

  function handleSubmit(e: any) {
    e.preventDefault();
    const {
      host,
      password,
      database_user,
      display_name,
      port,
      driver,
      is_default,
      database,
      extras,
    } = e.target;
    const payload = {
      name: display_name.value,
      db_host: host.value,
      db_port: port.value,
      db_driver: driver.value,
      db_user: database_user.value,
      db_database: database.value,
      db_password: password.value,
      is_default: is_default.checked,
      db_extras: extras.value ? JSON.parse(extras.value) : {},
    };
    const res = DbConfigService.createDbConnDbConfigConnectionsPost(payload);
    res
      .then((data) => {
        setHidden(true);
      })
      .catch((err) => {
        console.log(err);
        alert(err);
      });
  }
  return (
    <div className="modal modal-open text-white">
      <div className="modal-box">
        <div className="flex flex-row justify-between items-baseline">
          <h3>Add a database</h3>
          <button className="btn btn-square" onClick={() => setHidden(true)}>
            X
          </button>
        </div>
        <form className="form-control" onSubmit={(e) => handleSubmit(e)}>
          <label className="label cursor-pointer">
            <span className="label-text">Database Driver</span>
            <select
              name="driver"
              className="select select-bordered w-full max-w-xs"
            >
              <option value="snowflake">
                <span>
                  Snowflake
                  <FaSnowflake fill="white" />
                </span>
              </option>
              <option value="postgres">
                <span>
                  Postgres
                  <SiPostgresql fill="white" />
                </span>
              </option>
            </select>
          </label>
          <div className="w-full">
            {[
              "display_name",
              "database_user",
              "password",
              "host",
              "port",
              "database",
              "extras",
            ].map((x) => {
              return (
                <label className="label">
                  <span className="label-text capitalize">
                    {x !== "extras" ? x.replace("_", " ") : "Extras (Optional)"}
                  </span>
                  <input
                    name={x}
                    required={x !== "extras"}
                    pattern={x === "port" ? "\\d+" : ".*"}
                    type={x === "password" ? "password" : "text"}
                    placeholder={_placeholder(x)}
                    className="input input-bordered pass w-full max-w-xs"
                  />
                </label>
              );
            })}
          </div>
          <label className="label cursor-pointer flex flex-row w-full align-center">
            <span className="label-text flex-auto">Default?</span>
            <input name="is_default" type="checkbox" className="checkbox" />
          </label>
          <div className="flex flex-row-reverse">
            <button type="submit" className="btn btn-info text-white w-[50%]">
              Add connection
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const GeofencerPage = () => {
  // get all current connections for organization
  const [refresh, setRefresh] = useState(false);
  const [hideDbConnModal, setHideDbConnModal] = useState(true);
  const [conns, setConns] = useState<PublicDbCredential[]>([]);
  const [org, setOrg] = useState<Organization>();

  useEffect(() => {
    const res = DbConfigService.readDbConnsDbConfigConnectionsGet();
    res
      .then((data) => {
        setConns(data);
      })
      .catch((err) => {
        console.log(err);
      });
  }, [refresh]);

  useEffect(() => {
    const res = OrganizationsService.getActiveOrgOrganizationsActiveGet();
    console.log(res);
    res
      .then((data) => {
        setOrg(data);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <div className="relative w-full min-h-screen bg-slate-200">
      <DbConnectionModal
        hidden={hideDbConnModal}
        setHidden={setHideDbConnModal}
      />
      <div className="p-3 mx-auto bg-gradient-to-tr bg-blue-500">
        <Navbar />
      </div>
      <section className="max-w-5xl mx-auto my-5 space-y-1">
        <h1 className="text-xl font-bold">Database Configurations</h1>
        <div>
          <p>
            <strong>
              Please make sure you have reviewed the instructions before adding
              a connection.
            </strong>
          </p>
          <p>
            Viewing connections for the following organizations: {org?.name}.{" "}
          </p>
        </div>
        <div className="h-5">
          {conns && conns.length > 0 && (
            <table className="table text-white">
              <thead>
                <tr>
                  <th>Default</th>
                  <th>Name</th>
                  <th>Database Driver</th>
                  <th>Created</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {conns.map((conn: any) => (
                  <tr key={conn.id}>
                    <td>
                      <input
                        type="radio"
                        checked={conn.is_default}
                        onClick={() => {
                          alert("not implemented - set default connection");
                        }}
                      ></input>
                    </td>
                    <td>{conn.name}</td>
                    <td>{conn.db_driver}</td>
                    <td>{new Date(conn.created_at).toLocaleString()}</td>
                    <td>
                      <div className="btn-group">
                        <button
                          title="Test connection"
                          className="btn btn-square hover:bg-green-900"
                        >
                          <TbHeartPlus />
                        </button>
                        <button
                          title="Delete connection"
                          className="btn btn-square hover:bg-red-900"
                          onClick={(e) => {
                            DbConfigService.deleteDbConnDbConfigConnectionsUuidDelete(
                              conn.id
                            )
                              .then(() => {
                                setRefresh(!refresh);
                              })
                              .catch((err) => {
                                console.log(err);
                              });
                          }}
                        >
                          <TbTrash />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
              <button
                className="btn btn-info text-white"
                onClick={() => setHideDbConnModal(false)}
              >
                Add +{" "}
              </button>
            </table>
          )}
          {conns && conns.length === 0 && (
            <div className="max-w-5xl mx-auto">
              <p>
                No database connections are configured currently.{" "}
                <button
                  className="btn btn-info text-white"
                  onClick={() => setHideDbConnModal(false)}
                >
                  Add +{" "}
                </button>
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default GeofencerPage;
