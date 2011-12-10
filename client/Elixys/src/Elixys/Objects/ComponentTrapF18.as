package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentTrapF18 extends Component
	{
		// Constructor
		public function ComponentTrapF18(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = DEFAULT;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get CyclotronFlag():uint
		{
			return super.flash_proxy::getProperty("cyclotronflag");
		}
		public function set CyclotronFlag(value:uint):void
		{
			super.flash_proxy::setProperty("cyclotronflag", value);
		}
		
		public function get CyclotronFlagValidation():String
		{
			return super.flash_proxy::getProperty("cyclotronflagvalidation");
		}
		
		public function get TrapTime():uint
		{
			return super.flash_proxy::getProperty("traptime");
		}
		public function set TrapTime(value:uint):void
		{
			super.flash_proxy::setProperty("traptime", value);
		}
		
		public function get TrapTimeValidation():String
		{
			return super.flash_proxy::getProperty("traptimevalidation");
		}

		public function get TrapPressure():uint
		{
			return super.flash_proxy::getProperty("trappressure");
		}
		public function set TrapPressure(value:uint):void
		{
			super.flash_proxy::setProperty("trappressure", value);
		}
		
		public function get TrapPressureValidation():String
		{
			return super.flash_proxy::getProperty("trappressurevalidation");
		}
		
		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sTrapF18Details:String = JSONDataObject("cyclotronflag", CyclotronFlag);
			sTrapF18Details += JSONDataObject("traptime", TrapTime);
			sTrapF18Details += JSONDataObject("trappressure", TrapPressure, false);
			return sTrapF18Details;
		}

		// Type
		static public var TYPE:String = "TRAPF18";

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"TRAPF18\"," +
			"\"id\":0," +
			"\"name\":\"Trap F18\"," +
			"\"cyclotronflag\":0," +
			"\"traptime\":0," +
			"\"trappressure\":0}";
	}
}
