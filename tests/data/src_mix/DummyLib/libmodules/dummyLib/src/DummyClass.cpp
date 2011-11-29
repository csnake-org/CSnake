#include "DummyClass.h"

#include <Two.h>
#include <Three.h>
#include <Four.h>

namespace dummy
{

DummyClass::DummyClass() 
: m_count( 1 ) // warning: this value is used in the csnake test
{
	math::Two two;
	math::Three three;
	math::Four four;
    m_count += two.getTwo();
    m_count += three.getThree();
    m_count += four.getFour();
}

int DummyClass::getCount() const
{
   return m_count;
}

} // namespace dummy

