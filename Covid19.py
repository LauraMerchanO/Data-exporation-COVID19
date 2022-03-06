#!/usr/bin/env python
# coding: utf-8

# # **Covid 19 Data Exploration**
# 
# **Descargamos la data del sitio oficial del virus COVID 19** **https://ourworldindata.org/covid-deaths**. Esta exploracion es realizado en Azure Data Studio.

# In[2]:


Select *
From PORTAFOLIO.dbo.CovidDeaths
Where continent is not null 
order by 3,4


# Seleccionamos la data con la que vamos a trabajar, dondde el continente no sea nulo para trabajar.

# In[3]:


Select Location, date, total_cases, new_cases, total_deaths, population
From PORTAFOLIO.dbo.CovidDeaths
Where continent is not null 
order by 1,2


# <span style="font-size: 12px; white-space: pre;">Vamos a ver como se distribuye el total de casos vs el total de muertes.</span>
# 
# ### Probabilidad de morir por COVID.

# In[4]:


Select location, SUM(new_cases) as total_cases, SUM(new_deaths) as total_deaths, SUM(new_deaths)/SUM(New_Cases)*100 as DeathPercentage
From portafolio.dbo.CovidDeaths
--Where location like '%Colombia%'
Group by location
order by DeathPercentage desc


# Podemos ver que los paises en que mayor probabilidad hay de morir de COVID son Yemen, Vanuatu y Peru. Colombia se encuentra en el puesto 47.
# 
# ### Porcentaje de contraer COVID.

# In[5]:


Select location, SUM(new_cases) as total_cases, SUM(Population) as total_deaths, SUM(new_deaths)/SUM(Population)*100 as PercentPopulationInfected
From portafolio.dbo.CovidDeaths
--Where location like '%Colombia%'
Group by location
order by PercentPopulationInfected desc


# Podemos ver que los paises con mayor indice de infeccion son Peru, Bulgaria, Bosnia y Herzegovia. Colombia se encuentra en el puesto 20.
# 
#   
# 
# ### Paises con mayor tasa de infeccion comparada con la poblacion.

# In[6]:



Select Location, Population, MAX(total_cases) as HighestInfectionCount,  Max((total_cases/population))*100 as PercentPopulationInfected
From portafolio.dbo.CovidDeaths
Group by Location, Population
order by PercentPopulationInfected desc


# Encontramos entre los primeros puestos a Andorra, Montenegro y Gibraltar. Colombia se encuentra en el puesto 68.
# 
# ### Paises con mayor indice de muerte por poblacion.

# In[7]:


Select Location, MAX(Total_deaths) as TotalDeathCount
From portafolio.dbo.CovidDeaths
Where continent is not null 
Group by Location
order by TotalDeathCount desc


# Vemos que entre los primeros puestos esta EEUU, uno de los paises entre los que hubo mas excepticismo frente al virus, seguido por Brasil e India. Colombia se encuentra en el puesto 11.
# 
# Realizaremos un desglose por continente.
# 
# ### Continentes con el mayor recuento de muertes por población

# In[8]:



Select continent, MAX(cast(Total_deaths as int)) as TotalDeathCount
From portafolio.dbo.CovidDeaths
Where continent is not null 
Group by continent
order by TotalDeathCount desc


# Vemos que los continentes con mayor recuento de muertes por poblacion son Norte y Sur America y el continente con menor recuento es Oceania.

# ### Numeros globales.

# In[9]:


Select SUM(new_cases) as total_cases, SUM(new_deaths) as total_deaths, (SUM(new_deaths)/SUM(New_Cases))*100 as DeathPercentage
From portafolio.dbo.CovidDeaths
where continent is not null 
order by 1,2


# Podemos darnos cuenta que el porcentaje de muertes global fue del 1.75%
# 
#   
# 
# ## Total de poblacion VS Vacunados.
# 
# ### Porcentaje de poblacion de recibio al menos una vacuna contra el COVID.

# In[10]:


Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, SUM(vac.new_vaccinations) OVER (Partition by dea.Location Order by dea.location, dea.Date) as PeopleVaccinated

From portafolio.dbo.CovidDeaths dea
Join portafolio.dbo.CovidVaccinations vac
	On dea.location = vac.location
	and dea.date = vac.date
where dea.continent is not null 
order by PeopleVaccinated DESC


# Podemos ver que el epicentro del virus se encuentra entre los primeros puestos por su alto indice de personas vacunadas. Usaremos CTE para realizar el cálculo en la partición por en la consulta anterior

# In[11]:



With PopvsVac (Continent, Location, Date, Population, New_Vaccinations, PeopleVaccinated)
as
(
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations
, SUM(vac.new_vaccinations) OVER (Partition by dea.Location Order by dea.location, dea.Date) as PeopleVaccinated
From portafolio.dbo.CovidDeaths dea
Join portafolio.dbo.CovidVaccinations vac
	On dea.location = vac.location
	and dea.date = vac.date
where dea.continent is not null 
)
Select *, (PeopleVaccinated/Population)*100 as PercentPeopleVaccinated
From PopvsVac
order by PercentPeopleVaccinated DESC


# Podemos ver que el mayor porcentaje de vacunados fue del  2021-12-23 en Gibraltar, Europa. Sin embargo, el menor indice fue del 2021-12-06 en Hong Kong, Asia. Usaremos una tabla temporal para realizar el cálculo en la partición por en la consulta anterior.

# In[22]:


DROP Table if exists #PercentPopulationVaccinated
Create Table #PercentPopulationVaccinated
(
Continent nvarchar(255),
Location nvarchar(255),
Date datetime,
Population numeric,
New_vaccinations numeric,
PeopleVaccinated numeric
)

Insert into #PercentPopulationVaccinated
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations
SUM("(vac.new_vaccinations)", "OVER", "(Partition", "by", "dea.Location", "Order", "by", "dea.location,", "dea.Date)", "as", "PeopleVaccinated")

From portafolio.dbo.CovidDeaths dea
Join portafolio.dbo.CovidVaccinations vac
	On dea.location = vac.location
	and dea.date = vac.date
where dea.continent is not null 
--order by 2,3


Select *, (PeopleVaccinated/Population)*100 as PercentPeopleVaccinated
From #PercentPopulationVaccinated
order by PercentPeopleVaccinated Desc

