import { useEffect, useMemo, useState } from "react";

import { getDetectionCoverage } from "../../services/dashboardService";
import type { CoverageItem } from "../../services/dashboardService";

type StatusFilter = "All" | "Detected" | "Partial" | "Missed";

function getStatusLabel(item: CoverageItem): StatusFilter {
  if (
    item.detected > item.missed &&
    item.detected >= item.partial
  ) {
    return "Detected";
  }

  if (
    item.missed > item.detected &&
    item.missed >= item.partial
  ) {
    return "Missed";
  }

  return "Partial";
}

function getStatusClasses(status: StatusFilter) {
  switch (status) {
    case "Detected":
      return {
        card: "border-green-500 bg-green-50",
        badge: "border-green-300 bg-green-100 text-green-700",
        dot: "bg-green-500",
      };

    case "Partial":
      return {
        card: "border-yellow-500 bg-yellow-50",
        badge: "border-yellow-300 bg-yellow-100 text-yellow-700",
        dot: "bg-yellow-500",
      };

    case "Missed":
      return {
        card: "border-red-500 bg-red-50",
        badge: "border-red-300 bg-red-100 text-red-700",
        dot: "bg-red-500",
      };

    default:
      return {
        card: "border-gray-300 bg-gray-50",
        badge: "border-gray-300 bg-gray-100 text-gray-700",
        dot: "bg-gray-500",
      };
  }
}

function getItemKey(item: CoverageItem) {
  return `${item.tactic}-${item.technique}-${item.rule_name}`;
}

export default function MitreMatrix() {
  const [coverage, setCoverage] = useState<CoverageItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [statusFilter, setStatusFilter] =
    useState<StatusFilter>("All");

  const [searchTerm, setSearchTerm] = useState("");

  const [selectedKey, setSelectedKey] =
    useState<string | null>(null);

  useEffect(() => {
    const loadCoverage = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await getDetectionCoverage();

        setCoverage(data);
      } catch (err) {
        console.error(
          "Error loading MITRE coverage:",
          err
        );

        setError(
          "Unable to load MITRE coverage data."
        );
      } finally {
        setLoading(false);
      }
    };

    loadCoverage();
  }, []);

  const tactics = useMemo(() => {
    return Array.from(
      new Set(
        coverage
          .map((item) => item.tactic)
          .filter(Boolean)
      )
    ).sort();
  }, [coverage]);

  const filteredCoverage = useMemo(() => {
    const search = searchTerm.trim().toLowerCase();

    return coverage.filter((item) => {
      const calculatedStatus =
        getStatusLabel(item);

      const matchesStatus =
        statusFilter === "All" ||
        calculatedStatus === statusFilter;

      const matchesSearch =
        search === "" ||
        item.technique
          .toLowerCase()
          .includes(search) ||
        item.name
          .toLowerCase()
          .includes(search) ||
        item.rule_name
          .toLowerCase()
          .includes(search) ||
        item.tactic
          .toLowerCase()
          .includes(search) ||
        calculatedStatus
          .toLowerCase()
          .includes(search) ||
        (search === "detected" &&
          item.detected > 0) ||
        (search === "partial" &&
          item.partial > 0) ||
        (search === "missed" &&
          item.missed > 0);

      return (
        matchesStatus &&
        matchesSearch
      );
    });
  }, [
    coverage,
    statusFilter,
    searchTerm,
  ]);

  const selectedItem = coverage.find(
    (item) =>
      getItemKey(item) === selectedKey
  );

  const clearFilters = () => {
    setStatusFilter("All");
    setSearchTerm("");
    setSelectedKey(null);
  };

  if (loading) {
    return (
      <section className="mt-8 w-full min-w-0">
        <div className="rounded-lg border bg-white p-6">
          <h2 className="text-xl font-semibold">
            MITRE ATT&CK Matrix
          </h2>

          <p
            className="mt-2 text-sm text-gray-600"
            role="status"
          >
            Loading MITRE coverage...
          </p>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="mt-8 w-full min-w-0">
        <div
          className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-700"
          role="alert"
        >
          {error}
        </div>
      </section>
    );
  }

  return (
    <section className="mt-8 w-full min-w-0">
      {/* Header */}
      <div className="mb-5 flex min-w-0 flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <h2 className="text-xl font-semibold">
            MITRE ATT&CK Matrix
          </h2>

          <p className="mt-1 max-w-3xl break-words text-sm text-gray-600">
            Detection coverage mapped to MITRE ATT&CK
            tactics and techniques.
          </p>
        </div>

        <div className="w-full shrink-0 lg:w-52">
          <label
            htmlFor="mitre-status"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Status
          </label>

          <select
            id="mitre-status"
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(
                event.target.value as StatusFilter
              )
            }
            className="
              w-full
              rounded-md
              border
              border-gray-300
              bg-white
              px-3
              py-2
              text-sm
              outline-none
              transition
              focus:border-blue-500
              focus:ring-2
              focus:ring-blue-200
            "
          >
            <option value="All">
              All Statuses
            </option>

            <option value="Detected">
              Detected
            </option>

            <option value="Partial">
              Partial
            </option>

            <option value="Missed">
              Missed
            </option>
          </select>
        </div>
      </div>

      {/* Search and Filter Summary */}
      <div
        className="
          mb-5
          rounded-lg
          border
          bg-gray-50
          p-4
        "
      >
        <div className="flex min-w-0 flex-col gap-3 md:flex-row md:items-end">
          <div className="min-w-0 flex-1">
            <label
              htmlFor="mitre-search"
              className="mb-1 block text-sm font-medium text-gray-700"
            >
              Search
            </label>

            <input
              id="mitre-search"
              type="text"
              value={searchTerm}
              onChange={(event) =>
                setSearchTerm(
                  event.target.value
                )
              }
              placeholder="Search technique, tactic or rule..."
              className="
                w-full
                min-w-0
                rounded-md
                border
                border-gray-300
                bg-white
                px-3
                py-2
                text-sm
                outline-none
                transition
                focus:border-blue-500
                focus:ring-2
                focus:ring-blue-200
              "
            />
          </div>

          <button
            type="button"
            onClick={clearFilters}
            disabled={
              statusFilter === "All" &&
              searchTerm === "" &&
              selectedKey === null
            }
            className="
              w-full
              shrink-0
              rounded-md
              border
              border-gray-300
              bg-white
              px-4
              py-2
              text-sm
              font-medium
              text-gray-700
              transition
              hover:bg-gray-100
              focus:outline-none
              focus:ring-2
              focus:ring-blue-500
              disabled:cursor-not-allowed
              disabled:opacity-50
              md:w-auto
            "
          >
            Clear Filters
          </button>
        </div>

        <div className="mt-3 text-xs text-gray-500">
          Showing{" "}
          <span className="font-semibold text-gray-700">
            {filteredCoverage.length}
          </span>{" "}
          of{" "}
          <span className="font-semibold text-gray-700">
            {coverage.length}
          </span>{" "}
          techniques
        </div>
      </div>

      {/* Legend */}
      <div className="mb-6 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-gray-700">
        <div className="flex items-center gap-2">
          <span
            className="h-3 w-3 shrink-0 rounded-full bg-green-500"
            aria-hidden="true"
          />
          <span>Detected</span>
        </div>

        <div className="flex items-center gap-2">
          <span
            className="h-3 w-3 shrink-0 rounded-full bg-yellow-500"
            aria-hidden="true"
          />
          <span>Partial</span>
        </div>

        <div className="flex items-center gap-2">
          <span
            className="h-3 w-3 shrink-0 rounded-full bg-red-500"
            aria-hidden="true"
          />
          <span>Missed</span>
        </div>
      </div>

      {/* Matrix */}
      {filteredCoverage.length === 0 ? (
        <div className="rounded-lg border bg-white p-6 text-center text-sm text-gray-600">
          No MITRE coverage data matches the selected
          filters.
        </div>
      ) : (
        <div
          className="
            grid
            min-w-0
            grid-cols-1
            gap-5
            md:grid-cols-2
            xl:grid-cols-3
          "
        >
          {tactics.map((tactic) => {
            const tacticItems =
              filteredCoverage.filter(
                (item) =>
                  item.tactic === tactic
              );

            if (tacticItems.length === 0) {
              return null;
            }

            return (
              <div
                key={tactic}
                className="
                  min-w-0
                  rounded-lg
                  border
                  border-gray-200
                  bg-white
                  p-4
                  shadow-sm
                "
              >
                {/* Tactic Header */}
                <div className="mb-4 min-w-0 border-b border-gray-200 pb-3">
                  <h3 className="break-words text-base font-semibold text-gray-900">
                    {tactic}
                  </h3>

                  <p className="mt-1 text-xs text-gray-500">
                    {tacticItems.length}{" "}
                    {tacticItems.length === 1
                      ? "technique"
                      : "techniques"}
                  </p>
                </div>

                {/* Technique Cards */}
                <div className="space-y-3">
                  {tacticItems.map((item) => {
                    const calculatedStatus =
                      getStatusLabel(item);

                    const statusClasses =
                      getStatusClasses(
                        calculatedStatus
                      );

                    const itemKey =
                      getItemKey(item);

                    const isSelected =
                      selectedKey === itemKey;

                    return (
                      <button
                        key={itemKey}
                        type="button"
                        onClick={() =>
                          setSelectedKey(
                            itemKey
                          )
                        }
                        aria-pressed={isSelected}
                        className={`
                          block
                          w-full
                          min-w-0
                          rounded-lg
                          border-2
                          p-4
                          text-left
                          transition
                          hover:shadow-md
                          focus:outline-none
                          focus-visible:ring-2
                          focus-visible:ring-blue-500
                          focus-visible:ring-offset-2
                          ${statusClasses.card}
                          ${
                            isSelected
                              ? "ring-2 ring-blue-500 ring-offset-1"
                              : ""
                          }
                        `}
                      >
                        {/* Technique Header */}
                        <div
                          className="
                            flex
                            min-w-0
                            items-start
                            justify-between
                            gap-3
                          "
                        >
                          <div className="min-w-0 flex-1">
                            <div className="break-words text-sm font-bold text-gray-900">
                              {item.technique}
                            </div>
                          </div>

                          <span
                            className={`
                              inline-flex
                              shrink-0
                              items-center
                              gap-1.5
                              rounded-full
                              border
                              px-2
                              py-1
                              text-xs
                              font-semibold
                              ${statusClasses.badge}
                            `}
                          >
                            <span
                              className={`
                                h-2
                                w-2
                                shrink-0
                                rounded-full
                                ${statusClasses.dot}
                              `}
                              aria-hidden="true"
                            />

                            {calculatedStatus}
                          </span>
                        </div>

                        {/* Technique Name */}
                        <div className="mt-3 min-w-0 break-words text-sm font-medium leading-5 text-gray-800">
                          {item.name}
                        </div>

                        {/* Rule */}
                        <div className="mt-3 min-w-0 break-words text-xs leading-5 text-gray-600">
                          <span className="font-semibold text-gray-700">
                            Rule:
                          </span>{" "}
                          {item.rule_name}
                        </div>

                        {/* Counts */}
                        <div className="mt-4 grid grid-cols-3 gap-2 border-t border-gray-200/70 pt-3">
                          <div className="min-w-0">
                            <div className="text-sm font-semibold text-gray-900">
                              {item.detected}
                            </div>

                            <div className="text-[11px] text-gray-500">
                              Detected
                            </div>
                          </div>

                          <div className="min-w-0">
                            <div className="text-sm font-semibold text-gray-900">
                              {item.partial}
                            </div>

                            <div className="text-[11px] text-gray-500">
                              Partial
                            </div>
                          </div>

                          <div className="min-w-0">
                            <div className="text-sm font-semibold text-gray-900">
                              {item.missed}
                            </div>

                            <div className="text-[11px] text-gray-500">
                              Missed
                            </div>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Selected Technique */}
      {selectedItem && (
        <div
          className="
            mt-6
            min-w-0
            rounded-lg
            border
            border-gray-200
            bg-white
            p-4
            shadow-sm
            sm:p-5
          "
        >
          {/* Selected Header */}
          <div
            className="
              flex
              min-w-0
              flex-col
              gap-4
              sm:flex-row
              sm:items-start
              sm:justify-between
            "
          >
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-gray-500">
                Selected Technique
              </p>

              <h3 className="mt-1 break-words text-xl font-bold text-gray-900">
                {selectedItem.technique}
              </h3>

              <p className="mt-1 break-words text-sm text-gray-600">
                {selectedItem.name}
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                setSelectedKey(null)
              }
              className="
                w-full
                shrink-0
                rounded-md
                border
                border-gray-300
                bg-white
                px-3
                py-2
                text-sm
                font-medium
                text-gray-700
                transition
                hover:bg-gray-100
                focus:outline-none
                focus:ring-2
                focus:ring-blue-500
                sm:w-auto
              "
            >
              Clear
            </button>
          </div>

          {/* Selected Details */}
          <div
            className="
              mt-5
              grid
              min-w-0
              grid-cols-1
              gap-4
              sm:grid-cols-2
              lg:grid-cols-3
              xl:grid-cols-6
            "
          >
            <div className="min-w-0">
              <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                MITRE Tactic
              </p>

              <p className="mt-1 break-words text-sm font-medium text-gray-900">
                {selectedItem.tactic}
              </p>
            </div>

            <div className="min-w-0 xl:col-span-2">
              <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                Rule
              </p>

              <p className="mt-1 break-words text-sm font-medium text-gray-900">
                {selectedItem.rule_name}
              </p>
            </div>

            <div className="min-w-0">
              <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                Status
              </p>

              <p className="mt-1 text-sm font-semibold text-gray-900">
                {getStatusLabel(
                  selectedItem
                )}
              </p>
            </div>

            <div className="min-w-0">
              <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                Detected
              </p>

              <p className="mt-1 text-sm font-semibold text-gray-900">
                {selectedItem.detected}
              </p>
            </div>

            <div className="min-w-0">
              <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                Partial
              </p>

              <p className="mt-1 text-sm font-semibold text-gray-900">
                {selectedItem.partial}
              </p>
            </div>

            <div className="min-w-0">
              <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                Missed
              </p>

              <p className="mt-1 text-sm font-semibold text-gray-900">
                {selectedItem.missed}
              </p>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}