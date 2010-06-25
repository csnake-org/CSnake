#include "DummyClass2.h"

#include <Two.h>
#include <Three.h>

#include <Four.h>

namespace dummy
{

DummyClass2::DummyClass2() 
: m_count( 5 ) // warning: this value is used in the csnake test
{
	math::Two two;
	math::Three three;
	math::Four four;
    m_count += two.getTwo();
    m_count += three.getThree();
    m_count -= four.getFour();
}

int DummyClass2::getCount() const
{
   return m_count;
}

} // namespace dummy

