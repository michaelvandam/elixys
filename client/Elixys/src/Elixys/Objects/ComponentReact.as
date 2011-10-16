package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentReact extends Component
	{
		// Constructor
		public function ComponentReact(data:String = null, existingcontent:Object = null)
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
		public function get Reactor():uint
		{
			return super.flash_proxy::getProperty("reactor");
		}
		public function set Reactor(value:uint):void
		{
			super.flash_proxy::setProperty("reactor", value);
		}
		
		public function get ReactorValidation():String
		{
			return super.flash_proxy::getProperty("reactorvalidation");
		}

		public function get Position():String
		{
			return super.flash_proxy::getProperty("position");
		}
		public function set Position(value:String):void
		{
			super.flash_proxy::setProperty("position", value);
		}

		public function get PositionValidation():String
		{
			return super.flash_proxy::getProperty("positionvalidation");
		}

		public function get Duration():uint
		{
			return super.flash_proxy::getProperty("duration");
		}
		public function set Duration(value:uint):void
		{
			super.flash_proxy::setProperty("duration", value);
		}

		public function get DurationValidation():String
		{
			return super.flash_proxy::getProperty("durationvalidation");
		}

		public function get ReactionTemperature():Number
		{
			return super.flash_proxy::getProperty("reactiontemperature");
		}
		public function set ReactionTemperature(value:Number):void
		{
			super.flash_proxy::setProperty("reactiontemperature", value);
		}
	
		public function get ReactionTemperatureValidation():String
		{
			return super.flash_proxy::getProperty("reactiontemperaturevalidation");
		}
	
		public function get FinalTemperature():Number
		{
			return super.flash_proxy::getProperty("finaltemperature");
		}
		public function set FinalTemperature(value:Number):void
		{
			super.flash_proxy::setProperty("finaltemperature", value);
		}
	
		public function get FinalTemperatureValidation():String
		{
			return super.flash_proxy::getProperty("finaltemperaturevalidation");
		}
	
		public function get StirSpeed():uint
		{
			return super.flash_proxy::getProperty("stirspeed");
		}
		public function set StirSpeed(value:uint):void
		{
			super.flash_proxy::setProperty("stirspeed", value);
		}
	
		public function get StirSpeedValidation():String
		{
			return super.flash_proxy::getProperty("stirespeedvalidation");
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sReactDetails:String = JSONDataObject("reactor", Reactor);
			sReactDetails += JSONDataObject("position", Position);
			sReactDetails += JSONDataObject("duration", Duration);
			sReactDetails += JSONDataObject("reactiontemperature", ReactionTemperature);
			sReactDetails += JSONDataObject("finaltemperature", FinalTemperature);
			sReactDetails += JSONDataObject("stirspeed", StirSpeed, false);
			return sReactDetails;
		}

		// Type
		static public var TYPE:String = "REACT";

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"REACT\"," +
			"\"id\":0," +
			"\"name\":\"React\"," +
			"\"reactor\":0," +
			"\"position\":0," +
			"\"duration\":0," +
			"\"reactiontemperature\":0," +
			"\"finaltemperature\":0," +
			"\"stirspeed\":0}";
	}
}
