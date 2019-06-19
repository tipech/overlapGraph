




  def test_interval_random_values(self):
    interval = Interval(-5, 15)
    randoms = interval.random_values(5)
    #print(f'{interval}:')
    for value in randoms:
      #print(f'- {value}')
      self.assertTrue(interval.contains(value, inc_upper=False))

  def test_interval_random_interval(self):
    interval = Interval(-5, 15)
    randoms  = interval.random_intervals(5, Interval(0.25, 0.75))
    randoms += interval.random_intervals(5, Interval(0.25, 0.75), precision=0)
    #print(f'{interval}:')
    for subinterval in randoms:
      #print(f'- {subinterval}')
      self.assertTrue(subinterval in interval)



      
  def test_region_random_points(self):
    region2d = Region([-5, 0], [15, 10])
    region3d = Region([-5, 0, 0], [15, 10, 50])
    points2d = region2d.random_points(5)
    points3d = region3d.random_points(5)
    #print(f'{region2d}: random={points2d}')
    #print(f'{region3d}: random={points3d}')
    for point in points2d:
      self.assertTrue(region2d.contains(list(point), inc_upper=False))
    for point in points3d:
      self.assertTrue(region3d.contains(list(point), inc_upper=False))

  def test_region_random_regions(self):
    region = Region([-5, 0], [15, 10])
    randoms  = region.random_regions(5, Region([0.25, 0.25], [0.75, 0.75]))
    randoms += region.random_regions(5, Region([0.25, 0.25], [0.75, 0.75]), precision = 0)
    #print(f'{region}:')
    for subregion in randoms:
      #print(f'- {subregion}')
      self.assertTrue(subregion in region)