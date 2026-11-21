import React, { createContext, useContext, useState, useEffect } from 'react';
import { projectsApi } from '../api/client';
import { useAuth } from './AuthContext';

const ProjectContext = createContext();

export const ProjectProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchProjects = async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    try {
      const res = await projectsApi.list();
      setProjects(res.data);
      if (res.data.length > 0) {
        // Keep selected if still exists, or default to first
        setSelectedProject(prev => {
          if (prev) {
            const found = res.data.find(p => p.id === prev.id);
            if (found) return found;
          }
          return res.data[0];
        });
      } else {
        setSelectedProject(null);
      }
    } catch (err) {
      console.error("Error fetching projects:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchProjects();
    } else {
      setProjects([]);
      setSelectedProject(null);
    }
  }, [isAuthenticated]);

  const createProject = async (name, description) => {
    const res = await projectsApi.create(name, description);
    await fetchProjects();
    setSelectedProject(res.data);
    return res.data;
  };

  const deleteProject = async (id) => {
    await projectsApi.delete(id);
    await fetchProjects();
  };

  return (
    <ProjectContext.Provider value={{
      projects,
      selectedProject,
      setSelectedProject,
      loading,
      fetchProjects,
      createProject,
      deleteProject
    }}>
      {children}
    </ProjectContext.Provider>
  );
};

export const useProject = () => useContext(ProjectContext);
