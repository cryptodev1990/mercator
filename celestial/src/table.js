import { fake } from "./fake";

import avatar from "./avatar.svg";
import { useState } from "react";

function to100(num) {
  return Math.round(num * 100);
}

function toPercentage(num) {
  return Math.round(num * 100) + "%";
}

export const DriverTable = ({ drivers, positions }) => {
  const [selectAll, setSelectAll] = useState(false);
  return (
    <div className="h-[50vh] overflow-x-auto w-full overflow-y-scroll">
      <table class="table w-full">
        <thead>
          <tr>
            <th>
              <label>
                <input
                  checked={selectAll}
                  type="checkbox"
                  class="checkbox"
                  onSelect={() => setSelectAll(!selectAll)}
                />
              </label>
            </th>
            <th>Name</th>
            <th>Load ID</th>
            <th>Status</th>
            <th>% complete</th>
          </tr>
        </thead>
        <tbody>
          {drivers.map((driverId) => {
            const progress = positions.filter(
              (position) => position.driverId === driverId
            )[0].pctComplete;

            return (
              <tr key={driverId}>
                <th>
                  <label>
                    <input
                      checked={selectAll}
                      type="checkbox"
                      class="checkbox"
                    />
                  </label>
                </th>
                <td>
                  <div class="flex items-center space-x-3">
                    <div class="avatar">
                      <div class="mask mask-squircle w-12 h-12">
                        <img src={avatar} alt="Avatar Tailwind CSS Component" />
                      </div>
                    </div>
                    <div>
                      <div class="font-bold">{fake(driverId, "name")}</div>
                      <div class="text-sm opacity-50">California</div>
                    </div>
                  </div>
                </td>
                <td>{fake(driverId, "load")}</td>
                <td>{positions[driverId].state.replace("_", " ")}</td>
                <td>
                  <div
                    className="radial-progress"
                    style={{ "--value": to100(progress) }}
                  >
                    {toPercentage(progress)}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
        <tfoot>
          <tr>
            <th></th>
            <th>Name</th>
            <th>Load</th>
            <th>Status</th>
            <th>Progress</th>
          </tr>
        </tfoot>
      </table>
    </div>
  );
};
