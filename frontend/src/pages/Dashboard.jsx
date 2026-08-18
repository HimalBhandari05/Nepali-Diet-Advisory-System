import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  GENDER_CHOICES,
  ACTIVITY_LEVEL_CHOICES,
  FITNESS_GOAL_CHOICES,
  DIETARY_PREFERENCE_CHOICES,
  getChoiceLabel,
} from '../constants/profileChoices';

function Dashboard() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/api/profiles/user-profile/');
      if (response.data?.data) {
        setProfile(response.data.data);
      }
    } catch (err) {
      setError(
        err.response?.data?.message ||
          'Unable to load your profile summary. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const greetingName = user?.first_name
    ? user.first_name
    : user?.username || 'there';

  return (
    <div className="min-h-screen bg-[#FAF8F5] text-[#181715] flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-6xl w-full mx-auto py-10 px-6 sm:px-8 space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-4 border-b border-[#E5E1D8] pb-6">
          <div>
            <span className="font-code text-xs text-[#85837C] uppercase tracking-wider block mb-1">
              04 / Overview
            </span>
            <h1 className="font-editorial text-3xl sm:text-4xl text-[#181715] font-normal">
              Welcome back, {greetingName}
            </h1>
            <p className="font-ui text-sm text-[#57554F] mt-1">
              Your personalized Nepali diet and lifestyle advisory dashboard.
            </p>
          </div>

          {/* <Link
            to="/meals/new"
            className="inline-flex items-center justify-center font-ui text-sm font-medium bg-[#181715] hover:bg-[#244234] text-[#FAF8F5] px-5 py-2.5 rounded-xs transition-colors shadow-xs shrink-0 cursor-pointer"
          >
            + Log a Meal
          </Link> */}
        </div>

        {/* Meal Logging Quick Action Section */}
        <div className="bg-white border border-[#E5E1D8] p-6 sm:p-8 rounded-xs flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <span className="font-code text-[11px] text-[#85837C] uppercase tracking-wider block mb-1">
              Daily Nutrition
            </span>
            <h2 className="font-editorial text-2xl text-[#181715] font-normal mb-2">
              Track Today's Meals
            </h2>
            <p className="font-ui text-sm text-[#57554F] leading-relaxed">
              Record your breakfast, lunch, snacks, or dinner. Log traditional Nepali dishes like Dal Bhat, Tarkari, Momo, and more with instant nutrient analysis.
            </p>
          </div>
          <div className="shrink-0">
            <Link
              to="/meals/new"
              className="inline-flex items-center justify-center font-ui text-sm font-medium bg-[#244234] hover:bg-[#181715] text-[#FAF8F5] px-5 py-2.5 rounded-xs transition-colors cursor-pointer"
            >
              Start Meal Logging →
            </Link>
          </div>
        </div>

        {/* Profile Summary Section */}
        <div className="bg-[#FAF8F5] border border-[#E5E1D8] p-6 sm:p-8 rounded-xs">
          <div className="flex items-center justify-between border-b border-[#E5E1D8] pb-4 mb-6">
            <div>
              <span className="font-code text-xs text-[#85837C] uppercase tracking-wider block mb-0.5">
                Profile Summary
              </span>
              <h2 className="font-editorial text-2xl text-[#181715] font-normal">
                Health &amp; Lifestyle Profile
              </h2>
            </div>
            <Link
              to="/profile"
              className="font-ui text-xs font-medium text-[#181715] hover:text-[#244234] border border-[#E5E1D8] hover:border-[#244234] px-3.5 py-1.5 rounded-xs transition-colors bg-white cursor-pointer"
            >
              Edit Profile
            </Link>
          </div>

          {loading ? (
            <div className="py-8 text-center">
              <span className="font-code text-xs text-[#85837C] uppercase tracking-wider">
                Loading profile summary...
              </span>
            </div>
          ) : error ? (
            <div className="py-4 space-y-3">
              <div className="p-3 bg-[#FDF2F2] border border-[#9B2C2C]/20 text-[#9B2C2C] text-xs font-ui rounded-xs">
                {error}
              </div>
              <button
                type="button"
                onClick={fetchProfile}
                className="font-ui text-xs font-medium bg-[#181715] text-[#FAF8F5] py-1.5 px-3 rounded-xs cursor-pointer"
              >
                Retry
              </button>
            </div>
          ) : profile ? (
            <div className="space-y-6">
              {/* Physical Metrics Group */}
              <div>
                <span className="font-code text-[11px] text-[#85837C] uppercase tracking-wider block mb-3">
                  Physical Metrics
                </span>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                  <div className="bg-white border border-[#E5E1D8] p-3.5 rounded-xs">
                    <span className="font-ui text-[11px] text-[#85837C] uppercase tracking-wider block">
                      Age
                    </span>
                    <span className="font-ui text-base font-medium text-[#181715] mt-1 block">
                      {profile.age} <span className="text-xs text-[#85837C] font-normal">yrs</span>
                    </span>
                  </div>

                  <div className="bg-white border border-[#E5E1D8] p-3.5 rounded-xs">
                    <span className="font-ui text-[11px] text-[#85837C] uppercase tracking-wider block">
                      Gender
                    </span>
                    <span className="font-ui text-base font-medium text-[#181715] mt-1 block">
                      {getChoiceLabel(GENDER_CHOICES, profile.gender)}
                    </span>
                  </div>

                  <div className="bg-white border border-[#E5E1D8] p-3.5 rounded-xs">
                    <span className="font-ui text-[11px] text-[#85837C] uppercase tracking-wider block">
                      Height
                    </span>
                    <span className="font-ui text-base font-medium text-[#181715] mt-1 block">
                      {profile.height_cm} <span className="text-xs text-[#85837C] font-normal">cm</span>
                    </span>
                  </div>

                  <div className="bg-white border border-[#E5E1D8] p-3.5 rounded-xs">
                    <span className="font-ui text-[11px] text-[#85837C] uppercase tracking-wider block">
                      Weight
                    </span>
                    <span className="font-ui text-base font-medium text-[#181715] mt-1 block">
                      {profile.weight_kg} <span className="text-xs text-[#85837C] font-normal">kg</span>
                    </span>
                  </div>

                  <div className="bg-white border border-[#E5E1D8] p-3.5 rounded-xs col-span-2 sm:col-span-1">
                    <span className="font-ui text-[11px] text-[#85837C] uppercase tracking-wider block">
                      Target Weight
                    </span>
                    <span className="font-ui text-base font-medium text-[#181715] mt-1 block">
                      {profile.target_weight_kg ? (
                        <>
                          {profile.target_weight_kg}{' '}
                          <span className="text-xs text-[#85837C] font-normal">kg</span>
                        </>
                      ) : (
                        <span className="text-xs text-[#85837C] font-normal">None set</span>
                      )}
                    </span>
                  </div>
                </div>
              </div>

              {/* Lifestyle & Preferences Group */}
              <div>
                <span className="font-code text-[11px] text-[#85837C] uppercase tracking-wider block mb-3">
                  Lifestyle &amp; Preferences
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="bg-white border border-[#E5E1D8] p-3.5 rounded-xs">
                    <span className="font-ui text-[11px] text-[#85837C] uppercase tracking-wider block">
                      Activity Level
                    </span>
                    <span className="font-ui text-sm font-medium text-[#181715] mt-1 block">
                      {getChoiceLabel(ACTIVITY_LEVEL_CHOICES, profile.activity_level)}
                    </span>
                  </div>

                  <div className="bg-white border border-[#E5E1D8] p-3.5 rounded-xs">
                    <span className="font-ui text-[11px] text-[#85837C] uppercase tracking-wider block">
                      Fitness Goal
                    </span>
                    <span className="font-ui text-sm font-medium text-[#181715] mt-1 block">
                      {getChoiceLabel(FITNESS_GOAL_CHOICES, profile.fitness_goal)}
                    </span>
                  </div>

                  <div className="bg-white border border-[#E5E1D8] p-3.5 rounded-xs">
                    <span className="font-ui text-[11px] text-[#85837C] uppercase tracking-wider block">
                      Dietary Preference
                    </span>
                    <span className="font-ui text-sm font-medium text-[#181715] mt-1 block">
                      {getChoiceLabel(DIETARY_PREFERENCE_CHOICES, profile.dietary_preference)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
