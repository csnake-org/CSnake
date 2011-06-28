// -*- C++ -*-
// This is a test runner that initializes wxWidgets, so that wxWidgets objects can
// be created in tests.
//

// The CxxTest "world"
<CxxTest world>

#include <wx/wx.h>

class CxxTestApp: public wxApp {
public:
	bool OnInit();
};

IMPLEMENT_APP_CONSOLE(CxxTestApp)

bool CxxTestApp::OnInit()
{
	wxInitAllImageHandlers();
	CxxTest::ErrorPrinter().run();
	return true;
}
