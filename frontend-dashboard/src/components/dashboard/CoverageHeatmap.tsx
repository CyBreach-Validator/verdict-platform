import { useEffect, useMemo, useState } from "react";

import { getDetectionCoverage } from "../../services/dashboardService";
import type { CoverageItem } from "../../services/dashboardService";

type StatusFilter = "All" | "Detected" | "Partial" | "Missed";

function getStatusColor(item: CoverageItem) {
  if (item.detected > item.missed && item.detected >= item.partial) {
    return "bg-green-50 border-green-500";
  }

  if (item.missed > item.detected && item.missed >= item.partial) {
    return "bg-red-50 border-red-500";
  }

  return "bg-yellow-50 border-yellow-500";
}

function getStatusLabel(item: CoverageItem): StatusFilter {
  if (item.detected > item.missed && item.detected >= item.partial) {
    return "Detected";
  }

  if (item.missed > item.detected && item.missed >= item.partial) {
    return "Missed";
  }

  return "Partial";
}

function getCoveragePercentage(item: CoverageItem) {
  const total = item.detected + item.missed + item.partial;

  if (total === 0) {
    return 0;
  }

  return Math.round((item.detected / total) * 100);
}

export default function CoverageHeatmap() {
  const [coverage, setCoverage] = useState<CoverageItem[]>([]);
  const [loading, setLoading] = useState(true);

  const [statusFilter, setStatusFilter] =
    useState<StatusFilter>("All");

  const [tacticFilter, setTacticFilter] =
    useState("All");

  const [searchTerm, setSearchTerm] =
    useState("");

  const [appliedSearchTerm, setAppliedSearchTerm] =
    useState("");

  const [selectedTechnique, setSelectedTechnique] =
    useState<string | null>(null);

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

  const tactics = useMemo(() => {
    const uniqueTactics = Array.from(
      new Set(
        coverage
          .map((item) => item.tactic)
          .filter(Boolean)
      )
    );

    return uniqueTactics.sort();
  }, [coverage]);

  const filteredCoverage = useMemo(() => {
    const search = appliedSearchTerm.trim().toLowerCase();

    return coverage.filter((item) => {
      const matchesStatus =
        statusFilter === "All" ||
        getStatusLabel(item) === statusFilter;

      const matchesTactic =
        tacticFilter === "All" ||
        item.tactic === tacticFilter;

      const matchesSearch =
        search === "" ||
        item.technique.toLowerCase().includes(search) ||
        item.name.toLowerCase().includes(search) ||
        item.rule_name.toLowerCase().includes(search) ||
        item.status.toLowerCase().includes(search) ||
        (search === "detected" && item.detected > 0) ||
        (search === "partial" && item.partial > 0) ||
        (search === "missed" && item.missed > 0);

      return (
        matchesStatus &&
        matchesTactic &&
        matchesSearch
      );
    });
  }, [
    coverage,
    statusFilter,
    tacticFilter,
    appliedSearchTerm,
  ]);

  const selectedItem = coverage.find(
    (item) => item.technique === selectedTechnique
  );

  if (loading) {
    return (
      <div className="mt-8 min-w-0">
        <h2 className="text-xl font-semibold mb-4">
          Detection Coverage Heatmap
        </h2>

        <p>Loading coverage...</p>
      </div>
    );
  }

  return (
    <div className="mt-8 min-w-0 w-full">
      {/* Header */}
      <div className="flex flex-col gap-2 mb-5">
        <h2 className="text-xl font-semibold">
          Detection Coverage Heatmap
        </h2>

        <p className="text-sm text-gray-600 break-words">
          Interactive view of detection coverage across
          ATT&CK techniques and validation verdicts.
        </p>
      </div>

      {/* Filters */}
      <div
        className="
          grid
          grid-cols-1
          md:grid-cols-3
          gap-4
          mb-6
          p-4
          border
          rounded-lg
          bg-gray-50
        "
      >
        {/* Search */}
        <div className="min-w-0">
          <label
            htmlFor="coverage-search"
            className="block text-sm font-medium mb-1"
          >
            Search
          </label>

          <input
            id="coverage-search"
            type="text"
            value={searchTerm}
            onChange={(event) =>
              setSearchTerm(event.target.value)
            }
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                setAppliedSearchTerm(searchTerm);
              }
            }}
            placeholder="Search technique, rule, or verdict..."
            className="
              w-full
              min-w-0
              border
              rounded-md
              px-3
              py-2
              bg-white
              focus:outline-none
              focus:ring-2
              focus:ring-blue-500
            "
          />
        </div>

        {/* Status */}
        <div className="min-w-0">
          <label
            htmlFor="coverage-status"
            className="block text-sm font-medium mb-1"
          >
            Verdict Status
          </label>

          <select
            id="coverage-status"
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(
                event.target.value as StatusFilter
              )
            }
            className="
              w-full
              min-w-0
              border
              rounded-md
              px-3
              py-2
              bg-white
              focus:outline-none
              focus:ring-2
              focus:ring-blue-500
            "
          >
            <option value="All">All</option>
            <option value="Detected">Detected</option>
            <option value="Partial">Partial</option>
            <option value="Missed">Missed</option>
          </select>
        </div>

        {/* Tactic */}
        <div className="min-w-0">
          <label
            htmlFor="coverage-tactic"
            className="block text-sm font-medium mb-1"
          >
            MITRE Tactic
          </label>

          <select
            id="coverage-tactic"
            value={tacticFilter}
            onChange={(event) =>
              setTacticFilter(event.target.value)
            }
            className="
              w-full
              min-w-0
              border
              rounded-md
              px-3
              py-2
              bg-white
              focus:outline-none
              focus:ring-2
              focus:ring-blue-500
            "
          >
            <option value="All">All Tactics</option>

            {tactics.map((tactic) => (
              <option key={tactic} value={tactic}>
                {tactic}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 mb-5 text-sm">
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 rounded bg-green-200 border border-green-500 shrink-0" />
          Detected
        </div>

        <div className="flex items-center gap-2">
          <span className="w-4 h-4 rounded bg-yellow-200 border border-yellow-500 shrink-0" />
          Partial
        </div>

        <div className="flex items-center gap-2">
          <span className="w-4 h-4 rounded bg-red-200 border border-red-500 shrink-0" />
          Missed
        </div>
      </div>

      {/* Heatmap */}
      {filteredCoverage.length === 0 ? (
        <div className="border rounded-lg p-6 text-center text-gray-600 break-words">
          No coverage data matches the selected filters.
        </div>
      ) : (
        <div
          className="
            grid
            grid-cols-1
            sm:grid-cols-2
            lg:grid-cols-3
            gap-4
          "
        >
          {filteredCoverage.map((item) => {
            const coveragePercentage =
              getCoveragePercentage(item);

            const status = getStatusLabel(item);

            const isSelected =
              selectedTechnique === item.technique;

            return (
              <button
                key={`${item.technique}-${item.rule_name}`}
                type="button"
                onClick={() =>
                  setSelectedTechnique(item.technique)
                }
                className={`
                  min-w-0
                  w-full
                  text-left
                  border
                  rounded-lg
                  p-4 sm:p-5
                  transition
                  hover:shadow-md
                  cursor-pointer
                  ${getStatusColor(item)}
                  ${
                    isSelected
                      ? "ring-2 ring-blue-500"
                      : ""
                  }
                `}
              >
                {/* Card Header */}
                <div
                  className="
                    flex
                    flex-col
                    sm:flex-row
                    sm:justify-between
                    sm:items-start
                    gap-2
                    sm:gap-3
                    min-w-0
                  "
                >
                  <div className="min-w-0 flex-1">
                    <h3 className="text-lg font-bold break-words">
                      {item.technique}
                    </h3>

                    <p className="text-sm text-gray-700 break-words">
                      {item.name}
                    </p>
                  </div>

                  <span
                    className="
                      self-start
                      shrink-0
                      text-xs
                      font-semibold
                      border
                      rounded-full
                      px-2
                      py-1
                      bg-white
                    "
                  >
                    {status}
                  </span>
                </div>

                {/* Rule */}
                <p className="text-sm mt-3 font-medium break-words">
                  Rule: {item.rule_name}
                </p>

                {/* Tactic */}
                <p className="text-xs text-gray-600 mt-1 break-words">
                  Tactic: {item.tactic}
                </p>

                {/* Coverage */}
                <div className="mt-4">
                  <div className="flex justify-between gap-2 text-sm mb-1">
                    <span>Detection Coverage</span>

                    <span className="font-semibold shrink-0">
                      {coveragePercentage}%
                    </span>
                  </div>

                  <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500"
                      style={{
                        width: `${coveragePercentage}%`,
                      }}
                    />
                  </div>
                </div>

                {/* Counts */}
                <div className="grid grid-cols-3 gap-2 mt-4 text-sm">
                  <div className="min-w-0">
                    <div className="font-semibold">
                      {item.detected}
                    </div>

                    <div className="text-xs text-gray-600">
                      Detected
                    </div>
                  </div>

                  <div className="min-w-0">
                    <div className="font-semibold">
                      {item.partial}
                    </div>

                    <div className="text-xs text-gray-600">
                      Partial
                    </div>
                  </div>

                  <div className="min-w-0">
                    <div className="font-semibold">
                      {item.missed}
                    </div>

                    <div className="text-xs text-gray-600">
                      Missed
                    </div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}

      {/* Selected Technique Details */}
      {selectedItem && (
        <div className="mt-6 border rounded-lg p-4 sm:p-5 bg-white shadow-sm">
          <div
            className="
              flex
              flex-col
              sm:flex-row
              sm:justify-between
              sm:items-start
              gap-4
            "
          >
            <div className="min-w-0">
              <h3 className="text-lg font-semibold">
                Selected Technique
              </h3>

              <p className="text-xl font-bold mt-1 break-words">
                {selectedItem.technique}
              </p>

              <p className="text-sm text-gray-600 break-words">
                {selectedItem.name}
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                setSelectedTechnique(null)
              }
              className="
                self-start
                shrink-0
                px-3
                py-1
                border
                rounded-md
                text-sm
                hover:bg-gray-100
              "
            >
              Clear
            </button>
          </div>

          <div
            className="
              grid
              grid-cols-1
              sm:grid-cols-2
              md:grid-cols-4
              gap-4
              mt-5
            "
          >
            <div className="min-w-0">
              <p className="text-xs text-gray-500">
                Tactic
              </p>

              <p className="font-medium break-words">
                {selectedItem.tactic}
              </p>
            </div>

            <div className="min-w-0">
              <p className="text-xs text-gray-500">
                Rule
              </p>

              <p className="font-medium break-words">
                {selectedItem.rule_name}
              </p>
            </div>

            <div className="min-w-0">
              <p className="text-xs text-gray-500">
                Status
              </p>

              <p className="font-medium break-words">
                {getStatusLabel(selectedItem)}
              </p>
            </div>

            <div className="min-w-0">
              <p className="text-xs text-gray-500">
                Coverage
              </p>

              <p className="font-medium">
                {getCoveragePercentage(selectedItem)}%
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}