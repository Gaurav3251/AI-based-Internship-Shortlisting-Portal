import React, { useEffect, useState } from 'react';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Tooltip, Legend } from 'chart.js';
import { teacherAnalytics } from '../api/teacher.api';
import Loader from '../components/Loader.jsx';

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Tooltip, Legend);

const Analytics = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    teacherAnalytics().then(setData);
  }, []);

  if (!data) return <Loader />;

  const companyLabels = data.company_wise.map((c) => c.company_name);
  const companyCounts = data.company_wise.map((c) => c.shortlisted_count);

  const yearLabels = data.year_wise.map((y) => y.batch_year);
  const yearCounts = data.year_wise.map((y) => y.shortlisted_count);

  const statusLabels = ['Shortlisted', 'Under Review', 'Not Shortlisted'];
  const statusCounts = [data.total_shortlisted, data.total_under_review, data.total_not_shortlisted];

  return (
    <div>
      <div className="page-header">
        <div>
          <h4 className="page-title">Analytics</h4>
          <p className="page-subtitle">Track shortlisting performance and trends.</p>
        </div>
      </div>
      <div className="row g-3 mb-3">
        <div className="col-md-4"><div className="card p-3 metric-card"><div>Total Applications</div><h3>{data.total_applications}</h3></div></div>
        <div className="col-md-4"><div className="card p-3 metric-card"><div>Shortlisted</div><h3>{data.total_shortlisted}</h3></div></div>
        <div className="col-md-4"><div className="card p-3 metric-card"><div>Not Shortlisted</div><h3>{data.total_not_shortlisted}</h3></div></div>
      </div>
      <div className="card p-4 mb-3">
        <h5>Company-wise Shortlisted</h5>
        <Bar data={{ labels: companyLabels, datasets: [{ label: 'Shortlisted', data: companyCounts, backgroundColor: '#0d6efd' }] }} />
      </div>
      <div className="row g-3">
        <div className="col-lg-7">
          <div className="card p-4 h-100">
            <h5>Year-wise Shortlisted</h5>
            <Line data={{ labels: yearLabels, datasets: [{ label: 'Shortlisted', data: yearCounts, borderColor: '#0d6efd' }] }} />
          </div>
        </div>
        <div className="col-lg-5">
          <div className="card p-4 h-100">
            <h5>Application Status Split</h5>
            <Doughnut
              data={{
                labels: statusLabels,
                datasets: [{
                  data: statusCounts,
                  backgroundColor: ['#2563eb', '#f59e0b', '#ef4444'],
                  borderWidth: 0
                }]
              }}
              options={{
                plugins: { legend: { position: 'bottom' } },
                cutout: '65%'
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
