package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class SequenceComponent extends JSONObject
	{
		// Constructor
		public function SequenceComponent(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = m_sDefault;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Static type
		public static function get TYPE():String
		{
			return "sequencecomponent";
		}

		// Copy
		public function Copy(pSourceComponent:SequenceComponent):void
		{
			Name = pSourceComponent.Name;
			ID = pSourceComponent.ID;
			ComponentType = pSourceComponent.ComponentType;
			Note = pSourceComponent.Note;
			ValidationError = pSourceComponent.ValidationError;
		}
		
		// Data wrappers
		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function set Name(value:String):void
		{
			super.flash_proxy::setProperty("name", value);
		}

		public function get ID():uint
		{
			return parseInt(super.flash_proxy::getProperty("id"));
		}
		public function set ID(value:uint):void
		{
			super.flash_proxy::setProperty("id", value);
		}

		public function get ComponentType():String
		{
			return super.flash_proxy::getProperty("componenttype");
		}
		public function set ComponentType(value:String):void
		{
			super.flash_proxy::setProperty("componenttype", value);
		}

		public function get Note():String
		{
			return super.flash_proxy::getProperty("note");
		}
		public function set Note(value:String):void
		{
			super.flash_proxy::setProperty("note", value);
		}

		public function get ValidationError():Boolean
		{
			return (super.flash_proxy::getProperty("validationerror") == "true");
		}
		public function set ValidationError(value:Boolean):void
		{
			super.flash_proxy::setProperty("validationerror", value ? "true" : "false");
		}

		// Sequence component comparison function.  Returns true if the sequence components are equal, false otherwise.
		public static function CompareSequenceComponents(pSequenceComponentA:SequenceComponent, pSequenceComponentB:SequenceComponent):Boolean
		{
			if (pSequenceComponentA.Name != pSequenceComponentB.Name)
			{
				return false;
			}
			if (pSequenceComponentA.ID != pSequenceComponentB.ID)
			{
				return false;
			}
			if (pSequenceComponentA.ComponentType != pSequenceComponentB.ComponentType)
			{
				return false;
			}
			if (pSequenceComponentA.Note != pSequenceComponentB.Note)
			{
				return false;
			}
			if (pSequenceComponentA.ValidationError != pSequenceComponentB.ValidationError)
			{
				return false;
			}
			return true;
		}
		
		// Sequence component array comparison function.  Returns true if the arrays are equal, false otherwise.
		public static function CompareSequenceComponentArrays(pSequenceComponentsA:Array, pSequenceComponentsB:Array):Boolean
		{
			if (pSequenceComponentsA.length != pSequenceComponentsB.length)
			{
				return false;
			}
			else
			{
				var pSequenceComponentA:SequenceComponent, pSequenceComponentB:SequenceComponent;
				for (var i:int = 0; i < pSequenceComponentsA.length; ++i)
				{
					pSequenceComponentA = pSequenceComponentsA[i] as SequenceComponent;
					pSequenceComponentB = pSequenceComponentsB[i] as SequenceComponent;
					if (!CompareSequenceComponents(pSequenceComponentA, pSequenceComponentB))
					{
						return false;
					}
				}
			}
			return true;
		}

		// Default format
		private var m_sDefault:String = "{" +
			"\"type\":\"sequencecomponent\"," +
			"\"name\":\"\"," +
			"\"id\":\"\"," +
			"\"componenttype\":\"\"," +
			"\"note\":\"\"," +
			"\"validationerror\":\"\"}";
	}
}
