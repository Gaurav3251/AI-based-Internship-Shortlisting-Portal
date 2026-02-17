import React, { useEffect, useState } from 'react';
import { listInternships, myApplications } from '../api/student.api';
import InternshipCard from '../components/InternshipCard.jsx';
import Pagination from '../components/Pagination.jsx';
import Loader from '../components/Loader.jsx';

const StudentDashboard = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [query, setQuery] = useState('');
  const [appliedIds, setAppliedIds] = useState(new Set());

  const fetchData = async (pageNum = 1) => {
    setLoading(true);
    const [data, apps] = await Promise.all([
      listInternships({ page: pageNum, is_active: true }),
      myApplications()
    ]);
    const results = data.results || data;
    setItems(results);
    if (data.count) {
      setTotalPages(Math.ceil(data.count / 10));
    }
    const appList = apps.results || apps;
    setAppliedIds(new Set(appList.map((a) => a.internship?.id || a.internship)));
    setLoading(false);
  };

  useEffect(() => {
    fetchData(page);
  }, [page]);

  const filtered = items.filter((it) => {
    const needle = query.toLowerCase();
    return (
      it.company_name?.toLowerCase().includes(needle) ||
      it.internship_role?.toLowerCase().includes(needle) ||
      it.location?.toLowerCase().includes(needle)
    );
  });

  return (
    <div>
      <div className="page-header">
        <div>
          <h4 className="page-title">Student Dashboard</h4>
          <p className="page-subtitle">Explore internships tailored to your profile.</p>
        </div>
        <input
          className="form-control search-input"
          placeholder="Search by company, role, location"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {loading ? (
        <Loader />
      ) : (
        <div className="row g-3">
          {filtered.map((it) => (
            <div className="col-md-6" key={it.id}>
              <InternshipCard item={it} applied={appliedIds.has(it.id)} />
            </div>
          ))}
        </div>
      )}
      <div className="mt-3">
        <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
      </div>
    </div>
  );
};

export default StudentDashboard;
