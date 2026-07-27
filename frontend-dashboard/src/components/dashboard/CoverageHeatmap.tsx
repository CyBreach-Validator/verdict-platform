import { useEffect, useState } from "react";

import { getDetectionCoverage } from "../../services/dashboardService";
import type { CoverageItem } from "../../services/dashboardService";


function getStatusColor(item: CoverageItem) {

  if (item.detected > item.missed) {
    return "bg-green-100 border-green-500";
  }

  if (item.missed > item.detected) {
    return "bg-red-100 border-red-500";
  }

  return "bg-yellow-100 border-yellow-500";
}


export default function CoverageHeatmap() {

  const [coverage, setCoverage] = useState<CoverageItem[]>([]);
  const [loading, setLoading] = useState(true);


  useEffect(() => {

    getDetectionCoverage()
      .then((data) => {
        setCoverage(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error(
          "Error loading detection coverage:",
          error
        );

        setLoading(false);
      });

  }, []);


  if (loading) {
    return (
      <div className="mt-6">
        <h2 className="text-xl font-semibold">
          Detection Coverage Heatmap
        </h2>

        <p>
          Loading coverage...
        </p>
      </div>
    );
  }


  return (

    <div className="mt-8">

      <h2 className="text-xl font-semibold mb-4">
        Detection Coverage Heatmap
      </h2>


      {
        coverage.length === 0 ? (

          <p>
            No coverage data available.
          </p>

        ) : (

          <div
            className="
              grid
              grid-cols-1
              md:grid-cols-3
              gap-4
            "
          >

            {
              coverage.map((item) => (

                <div
                  key={item.technique}
                  className={`
                    border
                    rounded-lg
                    p-5
                    ${getStatusColor(item)}
                  `}
                >

                  <h3 className="text-lg font-bold">
                    {item.technique}
                  </h3>


                  <p className="text-sm mb-4">
                    {item.rule_name}
                  </p>


                  <div className="space-y-1">

                    <p>
                      🟢 Detected:
                      {" "}
                      {item.detected}
                    </p>


                    <p>
                      🔴 Missed:
                      {" "}
                      {item.missed}
                    </p>


                    <p>
                      🟡 Partial:
                      {" "}
                      {item.partial}
                    </p>

                  </div>

                </div>

              ))
            }

          </div>

        )
      }

    </div>

  );
}