--[[
Pandoc Lua filter to convert fenced divs to styled boxes
Converts semantic divs to LaTeX environments for PDF, keeps as divs for HTML
]]

function Div(el)
  local class = el.classes[1]
  
  -- Only process if the div has a recognized class
  if not class then
    return el
  end
  
  -- Map div classes to LaTeX environments
  local env_map = {
    didyouknow = "didyouknowbox",
    quiz = "quizbox",
    summary = "summarybox",
    casestudy = "casestudybox",
    keytakeaway = "summarybox"
  }
  
  local latex_env = env_map[class]
  
  if latex_env then
    if FORMAT:match 'latex' then
      -- For LaTeX/PDF output: convert to LaTeX environment
      local begin_env = '\\begin{' .. latex_env .. '}'
      local end_env = '\\end{' .. latex_env .. '}'
      
      -- Insert environment tags around the content
      table.insert(el.content, 1, pandoc.RawBlock('latex', begin_env))
      table.insert(el.content, pandoc.RawBlock('latex', end_env))
      
      return el.content
    else
      -- For HTML/EPUB: keep as div with class (can be styled with CSS)
      return el
    end
  end
  
  return el
end
