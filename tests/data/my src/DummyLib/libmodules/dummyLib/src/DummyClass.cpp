#include "DummyClass.h"

namespace dummy
{

DummyClass::DummyClass() 
: m_count( 10 ) // warning: this value is used in the csnake test
{
	// does nothing.
}

int DummyClass::getCount() const
{
   return m_count;
}

} // namespace dummy

